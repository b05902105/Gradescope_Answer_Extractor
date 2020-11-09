from requests_html import HTMLSession
import numpy as np
import pandas as pd
from sys import argv

def login(session, user, password, login_url):
	result = session.get(login_url)
	auth = result.html.xpath('//input[@name="authenticity_token"]/@value', first=True)

	payload = {
		'authenticity_token': auth,
		'session[email]': user,
		'session[password]': password,
	}
	session.post(login_url, data = payload)

def extract_submissions(session, URL):
	# Getting all submision elements

	all_submissions = session.get(URL).html.find('td.table--primaryLink-small')

	Name, Answer, Error = [], [], []

	for i, submission in enumerate(all_submissions):
		print('Extracting submissions: %03d/%03d' % (i+1, len(all_submissions)), end='\r')

		# Extracting links, user name
		link = list(submission.absolute_links)[0]
		Name.append(submission.text)

		# Getting & rendering the answer page.
		try:
			result = session.get(link)
			result.html.render(send_cookies_session=True, timeout=20)

			# Processing answer
			options = result.html.find('input[aria-checked]')
			raw_ans = np.array([1 if opt.attrs['aria-checked']=='true' else 0 for opt in options]).reshape(20, 6)

			# If no answer, fill-in 0
			ans = np.argmax(raw_ans, axis=1) + 1
			ans[np.sum(raw_ans, axis=1) == 0] = 0
			ans[ans == 6] = 0
			Answer.append(ans)
		except:
			print('\nError: Name:', Name[-1])
			Error.append(Name[-1])
			Answer.append(np.zeros(20))
	print()

	df = pd.DataFrame(np.array(Answer), columns=['Problem %02d' % n for n in range(1, 21)])
	df.insert(loc=0, column='Name', value=Name)

	return df.sort_values(by=['Name']), Error

def get_student_info(session, URL):
	all_students = session.get(URL).html.find('tr')
	
	Name, Email, Sid, Time = [], [], [], []
	for i, student in enumerate(all_students):
		print('Extracting students info: %03d/%03d' % (i+1, len(all_students)), end='\r')
		status = student.find('td')

		# If finding, this student didn't submit any answer.
		if not status[-1].find('td[class=table--hiddenColumn]'):
			Name.append(status[0].text)
			Email.append(status[1].text)
			Sid.append(Email[-1].split('@')[0])
			Time.append(status[-1].text)
	print()
	df = pd.DataFrame({'Name': Name, 'Email': Email, 'Student ID': Sid, 'Time': Time})
	return df.sort_values(by = ['Name'])


if __name__ == '__main__':

	# Arguments processing
	if len(argv) != 2:
		print('Usage: python extracting.py [config file]')
		exit(0)
	args = dict()
	with open(argv[1], 'r') as f:
		for line in f:
			line = line.split(',')
			args[line[0]] = line[1].strip()

	USER = args['USER']
	PASS = args['PASS']
	LOGIN_URL = args['LOGIN_URL']
	SUBMISSION_URL = args['SUBMISSION_URL']
	INFO_URL = args['INFO_URL']

	# Starting
	session = HTMLSession()
	login(session, user=USER, password=PASS, login_url=LOGIN_URL)

	answer_df, error = extract_submissions(session, SUBMISSION_URL)
	student_df = get_student_info(session, INFO_URL)

	df = pd.concat([student_df, answer_df], axis=1)
	df.to_csv('answer.csv', index=False)

	# Export Error List
	error_frame = student_df.loc(error)
	error_frame.to_csv('error.csv', index=False)
	
