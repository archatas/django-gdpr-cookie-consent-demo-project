# Django GDPR Cookie Consent Demo Project

## Description

This project shows an example of [Django GDPR Cookie Consent](https://websightful.gumroad.com/l/django-gdpr-cookie-consent) app integration into a Django project.

As stated by [GDPR cookie law](https://gdpr.eu/cookies/), websites that serve content for people from European Union must get consent from website visitors before storing any cookies that are not strictly necessary for the website to function. Not complying with GDPR laws can result in a fine of up to €20 million or 4% of the company's annual revenue, whichever is greater.

Django GDPR Cookie Consent app allows you to set up a modal dialog for cookie explanations and preferences. When a specific cookie section is accepted, the widget loads or renders HTML snippets related to that section. For example, if a visitor approved Performance cookies, they would get Google Analytics loaded.

Using the Django GDPR Cookie Consent app, you store the following information about the cookies in Django project settings:

- What are the cookie sections (e.g. "Essential", "Functionality", "Performance", "Marketing")? Are they bounded with any conditional HTML snippets?
- What are the cookie providers within each section (e.g., "This website," "Google Analytics," "Facebook," "Youtube," etc.)?
- What are the cookies set by each of those providers?

Descriptions for sections, providers, or cookies are translatable. User preferences are saved in a cookie too. If a particular section is unselected later, cookies related to that section are attempted to get deleted.

## Demo

[![Using Django GDPR Cookie Consent](https://raw.githubusercontent.com/archatas/django-gdpr-cookie-consent-demo-project/primary/assets/video-screenshot.png)](https://youtu.be/nSCdNCHQKUY)

This video was made using the Selenium tests that are included in this project's code.

## Django GDPR Cookie Consent in Production

Django GDPR Cookie Consent is used at

- [1st things 1st](https://www.1st-things-1st.com)
- [DjangoTricks](https://www.djangotricks.com)

## How to Install this Demo Project

### 1. Create and activate a virtual environment

```shell
$ python3 -m venv venv
$ source venv/bin/activate
```

### 2. Purchase and download Django GDPR Cookie Consent app

[Get Django GDPR Cookie Consent from Gumroad](https://websightful.gumroad.com/l/django-gdpr-cookie-consent).

Put the `*.whl` file into `private_wheels/` directory.

### 3. Download appropriate Webdriver for your Chrome version

Download and install [Chrome browser](https://www.google.com/chrome/).

Then [download the webdriver matching your Chrome version](https://chromedriver.chromium.org/downloads) and extract it to `drivers/` directory.

### 4. Install pip requirements into your virtual environment

With the virtual environment activated, install pip requirements:

```shell
(venv)$ pip install -r requirements.txt
```

### 5. Run database migrations and collect static files

With the virtual environment activated, run database migrations:

```shell
(venv)$ python manage.py migrate
(venv)$ python manage.py collectstatic --noinput
```

### 6. Run Selenium tests

With the virtual environment activated, run the tests:

```shell
(venv)$ python manage.py test
```

### 7. Browse

With the virtual environment activated, run development server:

```shell
(venv)$ python manage.py runserver
```

Browse the local website under <http://127.0.0.1:8000> and inspect the cookies in web development tools.

Compare the functionality with the source code.

## Disclaimer

The actual website's compliance with the GDRP Cookie Law depends on the configuration of each use case. The Django GDPR Cookie Consent app provides the mechanism to make that possible, but it's up to you how you configure and integrate it.

## Contact

For technical questions or bug reports, please contact Aidas Bendoraitis at <https://www.djangotricks.com/feedback/>.
