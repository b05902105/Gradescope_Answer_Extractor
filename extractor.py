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

def extract_submission(session, URL):
	result = session.get(URL)
	result.html.render(send_cookies_session=True, timeout=100)

	options = result.html.find('input[aria-checked]')
	raw_ans = np.array([1 if opt.attrs['aria-checked'] == 'true' else 0 for opt in options]).reshape(20, 6)

	ans = np.argmax(raw_ans, axis=1) + 1
	ans[np.sum(raw_ans, axis=1) == 0] = 0
	ans[ans == 6] = 0
	return ans
		
def get_student_info(session, student_list):
	
	Name, Email, Sid, Time, Answer = [], [], [], [], []
	for i, student in enumerate(student_list):
		print('Extracting students info: %03d/%03d' % (i+1, len(student_list)), end='\r')
		status = student.find('td')

		# If finding, this student didn't submit any answer.
		if not status[-1].find('td[class=table--hiddenColumn]'):
			Name.append(status[0].text)
			Email.append(status[1].text)
			Sid.append(Email[-1].split('@')[0])
			Time.append(status[-1].text)
			Answer.append(extract_submission(session, list(status[0].absolute_links)[0]))
	print()

	if Name:
		df = pd.DataFrame({'Name': Name, 'Email': Email, 'Student ID': Sid, 'Time': Time})
		ans_df = pd.DataFrame(np.array(Answer), columns=['Problem %02d' % n for n in range(1, 21)])
		return pd.concat([df, ans_df], axis=1)
	return None

def get_student_list(session, URL):
	return session.get(URL).html.find('tr')


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

	partial_df = list()
	student_list = get_student_list(session, INFO_URL)
	print('Total # students: %03d' % (len(student_list)))

	for i in range(0, len(student_list), 100):

		print('Students %03d ~ %03d' % (i+1, min(i+100, len(student_list))))
		
		df = get_student_info(session, student_list[i: i+100])
		partial_df.append(df)

		# Restarting
		session.close()
		session = HTMLSession()
		login(session, user=USER, password=PASS, login_url=LOGIN_URL)

	partial_df = list(filter(None, partial_df))
	total_df = pd.concat(partial_df, axis=0)
	total_df.to_csv('answer.csv', index=False)
