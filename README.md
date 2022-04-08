# Ireland.ie Wagtail CMS

## Initial setup

Clone this repo: be sure to switch to the `develop` branch.

```bash
git clone git@github.com:ogcio/ireland-ie-wagtail.git
cd ireland-ie-wagtail
git checkout develop
```

## Setting up a local build

This repository includes `docker-compose` configuration for running the project in local Docker containers.

## Docker and docker-compose (recommended)

### Dependencies

The following are required to run the local environment. The minimum versions specified are confirmed to be working:
if you have older versions already installed they _may_ work, but are not guaranteed to do so.

- [Docker](https://www.docker.com/), version 19.0.0 or up
  - [Docker Desktop for Mac](https://hub.docker.com/editions/community/docker-ce-desktop-mac) installer
  - [Docker Engine for Linux](https://hub.docker.com/search?q=&type=edition&offering=community&sort=updated_at&order=desc&operating_system=linux) installers
- [Docker Compose](https://docs.docker.com/compose/), version 1.24.0 or up
  - [Install instructions](https://docs.docker.com/compose/install/) (Linux-only: Compose is already installed for Mac users as part of Docker Desktop.)

## Running the local build for the first time

If you are using Docker Desktop, ensure the Resources:File Sharing settings allow the cloned directory to be mounted in the web container (avoiding `mounting` OCI runtime failures at the end of the build step).

Starting a local build can be done by running:

```bash
docker-compose build
docker-compose up -d web
```

This will start the containers in the background, but not Django. To do this, connect to the web container with:

```bash
docker-compose exec web bash
```

To run all Django commands always access the running container first and run the commands from the container command line.

The to start Django run:

```bash
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver 0.0.0.0:8000
```

The site will be available on the host machine at: http://127.0.0.1:8000/

You will only need to run the `migrate` and `createsuperuser` commands on initial setup when a new development database has been created.

Upon first starting the container, the static files may not exist, or may be out of date. See [frontend tooling](#frontend-tooling) for set-up instructions and to resolve this, simply run `npm run build`.

If you `git pull` any new changes also run `npm run build` to update your local compiled static files so you will see any changes reflected with styling etc.

## Frontend tooling

Here are the common commands: The commands should be run from a terminal on your local machine

```bash
# Install front-end dependencies.
npm install
# Start the Webpack build in watch mode, without live-reload.
npm run start
# Do a one-off Webpack development build.
npm run build
# Do a one-off Webpack production build.
npm run build:prod
```

Node v14 is the correct version to use for building the frontend. There is a `.nvmrc` file you can use to switch to the correct node version: run `nvm use` in your terminal before the commands above.

- All static source files are located at [static_src](/static_src/) 
- When npm commands are run, generated static assets are saved to [static_compiled](/static_compiled/)

### Python and virtualenv (legacy)

- create virtual environment `python3 -m venv .venv`
- activate virtual environment `source .venv/bin/activate`
- install dependencies `pip install -r requirements.txt`
- copy environment variables file `cp app/.env_example app/.env`
- apply migrations `python3 manage.py migrate`
- run server `python3 manage.py runserver 8000`

The site will be available at `http://localhost:8000`

## Other Documentation

- [Continuous Integration](/docs/continuous-integration.md)
- [Contributing To The Project](/docs/contributing.md)
- [Infrastructure](/docs/infrastructure.md)
- [Project Conventions](/docs/project-conventions.md)
