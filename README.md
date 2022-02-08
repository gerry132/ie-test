# Ireland.ie Wagtail CMS


## Setup for local development

- clone this repo
- navigate to directory with manage.py file in it
- create virtual environment `python3 -m venv .venv`
- activate virtual environment `source .venv/bin/activate`
- install dependencies `pip install -r requirements.txt`
- copy environment variables file `cp app/.env_example app/.env`
- apply migrations `python3 manage.py makemigrations`
- migrate `python3 manage.py migrate`
- run server `python3 manage.py runserver 8000`


## Environment variables

### APP
- ALLOWED_HOSTS - Allowed hosts list as json string , defaults to `["\*"]`, required value
- DEBUG - debug value, defaults to `True`, required value
- DEBUG_TOOLBAR - enable debug toolbar
- SECRET_KEY - secret key, required value

### Database
DATABASE_URL - database url e.g. postgres:// defaults to `''` and uses sqlite3

### S3 Support
- USE_S3 - Set to True if planning to use s3 bucket for static files, defaults to `False`
- AWS_ACCESS_KEY_ID - AWS access key id if planning to use s3 bucket for static files
- AWS_SECRET_ACCESS_KEY - AWS secret access key if planning to use s3 bucket for static files
- AWS_STATIC_BUCKET_NAME - AWS bucket name if planning to use s3 bucket for static files

### Wagtail
- BASE_URL - Base URL for wagtail to use, defaults to `http://localhost:8000`

### Caching
- USE_CACHE - Set to True if planning to use cache, defaults to `False`
- CACHE_ADDRESS - Base URL for cache backend, defaults to blank


## Running terraform

Common environment has been set up to pull alpine3.11 from docker hub and create local image of it (this will avoid docker hub terminating connections on frequent builds)

- go to `infrastructure/terraform/<env>/`
- in `.aws` create `.conf` and `.credentials` from coresponding `*.example` files
- create `ireland-ie-infrastructure` bucket in S3
- run `terraform init`
- run `terraform-apply`
- go to aws console and update SSM parameters for `AWS_SECRET_ACCESS_KEY` , `AWS_ACCESS_KEY_ID` , `DOCKER_IMAGE_URL` with your environment values
- run your build procedures and deploy images to ecs from here


## AWS infrastructure
- Public subnets for website and admin panel
- Private subnet for db, redis, ecs
- 2 ELBs for filtered admin site traffic and unfiltered traffic for public website
- ELB rules set to serve system on 2 domains e.g. content.ireland.ie and ireland.ie
- Elastic Cache with Redis
- RDS with Postgres DB
- ECS with cluster per environment
- ECR repo per environment
- S3 for static files, file upload and logging
- ECS, LB logging to S3
