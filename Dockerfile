ARG DOCKER_IMAGE_URL=alpine:3.20.2

FROM ${DOCKER_IMAGE_URL}

# init

RUN mkdir /app
RUN mkdir /static
WORKDIR /app
COPY requirements.txt /app/
COPY update_indexes.sh /app/
COPY docker-entrypoint.sh /app/
COPY publish_scheduled_items.sh /app/

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

ARG AWS_REGION
ARG AWS_ACCOUNT_ID
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

RUN pip install --upgrade pip --break-system-packages
RUN pip install awscli --break-system-packages

RUN aws codeartifact login \
      --tool pip \
      --repository wagtail-pypi \
      --domain hydrogen \
      --domain-owner "$AWS_ACCOUNT_ID" \
      --region "$AWS_REGION"

RUN pip install -r requirements.txt --break-system-packages


RUN ["chmod", "+x", "/app/docker-entrypoint.sh"]
RUN ["chmod", "+x", "/app/update_indexes.sh"]
RUN ["chmod", "+x", "/app/publish_scheduled_items.sh"]



# clean
RUN apk del -r \
    curl-dev \
    postgresql \
    python3-dev

# prep
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
COPY . /app/
