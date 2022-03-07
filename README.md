# Ireland.ie Wagtail CMS

## Setup for local development

Clone this repo: be sure to use the main branch. *At this time the default branch is develop, that may change soon.*

```bash
git clone git@github.com:ogcio/ireland-ie-wagtail.git
cd ireland-ie-wagtail
git checkout main
```

### Python and Wagtail

- create virtual environment `python3 -m venv .venv`
- activate virtual environment `source .venv/bin/activate`
- install dependencies `pip install -r requirements.txt`
- copy environment variables file `cp app/.env_example app/.env`
- apply migrations `python3 manage.py migrate`
- run server `python3 manage.py runserver 8000`

The site will be available at `http://localhost:8000`

### Frontend, Node and NPM

To build the frontend assets run the following commands:

NVM is available to set up the node version correctly.

```bash
nvm use
npm install
npm run build
```

## Contributing to the project

Currently the default branch is set to develop. When starting a new piece of work make sure to create your working branch based off the main branch. `git checkout main`

To start a new feature first create the new branch you'll be working on.

```bash
git checkout -b [my-branch]
```

While building the new feature it's recommended to `rebase` your branch on the main branch regularly to pick any changes merged to main by other developers and fix any conflicts.

```bash
git rebase main
```

When your work is complete you should push your changes to the github repository.

- Go to GITHUB and make a new pull request for your work/branch. Ensure the target branch is set to `main`
- **Include a link to the ticket you are working on** and add any other information that will assist a developer with the code review.
- Add a label `Main merge` to the pull request.
- Create the pull request and ask someone to review it.

### Code Review

#### Develop Pull Request

When your work has been code reviewed and is ready for acceptance testing you should create a second pull request but this time the target branch should be set to `develop`. Make sure not to make any changes to this pull request, it should be at the same commit position as the previous pull request you targeted at `main`.

Add a label `Develop merge` to the pull request.

#### Get approval to merge this pull request to develop

You will need to get approval to merge the `develop` pull request. There should be no need for any feedback here but the reviewer should check that no changes have been made when comparing with the `main` pull request.

#### Github Actions

There are tests to check any pushes to the `develop` or `main` branches. If the test fail you won't be able to merge the pull request.

- *The tests check for code formatting and any missing migrations.*

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

## Running the app locally

Build and run using [Docker compose](https://docs.docker.com/compose/):

```bash
docker compose up --build
```

Then access the app on http://localhost:8000.

