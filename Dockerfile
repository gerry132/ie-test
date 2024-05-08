ARG DOCKER_IMAGE_URL=alpine:3.11

FROM ${DOCKER_IMAGE_URL}

# init
VOLUME ["/tmp"]
RUN --mount=type=bind,target=/tmp
RUN mkdir /app
RUN mkdir /static
WORKDIR /app
COPY requirements.txt /app/
COPY docker-entrypoint.sh /app/

# setup
RUN apk update
RUN apk upgrade
RUN apk --no-cache add \
    bash \
    build-base \
    curl \
    curl-dev \
    gettext \
    postgresql-client \
    postgresql-dev \
    python3 \
    python3-dev \
    git \
    libffi-dev \
    openssl-dev \
    jpeg-dev \
    zlib-dev
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

RUN ["chmod", "+x", "/app/docker-entrypoint.sh"]
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]

# clean
RUN apk del -r \
    curl-dev \
    postgresql \
    python3-dev

# prep
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
COPY . /app/
