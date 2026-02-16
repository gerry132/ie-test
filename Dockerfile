ARG DOCKER_IMAGE_URL=alpine:3.20.2

FROM ${DOCKER_IMAGE_URL}

# init

RUN mkdir /app
RUN mkdir /static
WORKDIR /app
COPY requirements.txt /app/
ADD tasks /app/tasks

# setup
RUN apk update
RUN apk upgrade

RUN apk --no-cache --update add \
    bash \
    build-base \
    curl \
    curl-dev \
    cython \
    gettext \
    postgresql-client \
    postgresql-dev \
    python3 \
    libxml2-dev \
    python3-dev \
    py-pip \
    gcc \
    libheif \
    git \
    libffi-dev \
    openssl-dev \
    jpeg-dev \
    zlib-dev

RUN pip install awscli --break-system-packages

ARG CODEARTIFACT_DOMAIN=uat
ARG CODEARTIFACT_DOMAIN_OWNER=100350071169
ARG CODEARTIFACT_REPOSITORY=python
ARG AWS_DEFAULT_REGION=eu-west-1

RUN aws codeartifact login \
    --tool pip \
    --domain ${CODEARTIFACT_DOMAIN} \
    --domain-owner ${CODEARTIFACT_DOMAIN_OWNER} \
    --repository ${CODEARTIFACT_REPOSITORY} \
    --region ${AWS_DEFAULT_REGION}

RUN pip install --upgrade pip --break-system-packages
RUN pip install -r requirements.txt --break-system-packages


RUN ["chmod", "+x", "/app/tasks/docker-entrypoint.sh"]
RUN ["chmod", "+x", "/app/tasks/update_indexes.sh"]
RUN ["chmod", "+x", "/app/tasks/publish_scheduled_items.sh"]



# clean
RUN apk del -r \
    curl-dev \
    postgresql \
    python3-dev

# prep
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
COPY . /app/
