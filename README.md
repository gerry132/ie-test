# G2G sites wagtail cms


## Setup for local development

- clone this repo
- navigate to directory with manage.py file in it
- create virtual environment `python3 -m venv .venv`
- install dependencies `pip install -r requirements.txt`
- copy environment variables file `cp app/.env.example app/.env`
- apply migrations `python3 manage.py makemigrations`
- run server `python3 manage.py runserver 8000`


## Environment variables

### APP
ALLOWED_HOSTS - Allowed hosts list as json string , defaults to `["\*"]`, required value
DEBUG - debug value, defaults to `True`, required value
DEBUG_TOOLBAR - enable debug toolbar
SECRET_KEY - secret key, required value

### Database
DATABASE_URL - database url e.g. postgres:// defaults to `''` and uses sqlite3

### S3 Support
USE_S3 - Set to True if planning to use s3 bucket for static files, defaults to `False`
AWS_ACCESS_KEY_ID - AWS access key id if planning to use s3 bucket for static files
AWS_SECRET_ACCESS_KEY - AWS secret access key if planning to use s3 bucket for static files
AWS_STATIC_BUCKET_NAME - AWS bucket name if planning to use s3 bucket for static files

### Wagtail
BASE_URL - Base URL for wagtail to use, defaults to `http://localhost:8000`

