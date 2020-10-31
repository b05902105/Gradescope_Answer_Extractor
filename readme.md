# Gradescope Online Assignment Submission Extractor

A submission extractor specialized for gradescope online asssignment.

## Packages

```
pip install -r requirements.txt --force-reinstall
```

## Usage

1. Set the configuration:

	Please fill-in the following config information in `config` before extracting. (Please use "," as a delimiter)

	* **LOGIN_URL**: In general, it should be `https://www.gradescope.com/login`.
	* **INFO_URL**: The url recording students information. In general, it should be the `Review Grades` page.
	* **SUBMISSION_URL**: The url recording students' submissions. In general, it should be the `Manage Submissions` page.
	* **USER**: The user's email, please make sure that you have sufficient permissions.
	* **PASS**: The user's password, please make sure that you have sufficient permissions.

	E.G., 

	```
	LOGIN_URL, https://www.gradescope.com/login
	INFO_URL, https://www.gradescope.com/courses/111/assignments/222/review_grades
	SUBMISSION_URL, https://www.gradescope.com/courses/111/assignments/222/submissions
	USER, haha@haha.edu.tw
	PASS, hahahaha
	```

2. Execute the main process

	```
	python3 extracting.py [config file]
	```

## Exception

If you're faced with some exceptions such that:

```
TypeError: render() got an unexpected keyword argument 'send_cookies_session'
```

It raises because of the version difference of `requests_html`

Please doing the following operations

```
pip uninstall requests_html
git clone https://github.com/psf/requests-html
cd requests-html
python setup.py install
cd ..
rm -rf requests-html
```

By the above procedure, you can update your request-html to the latest version.
