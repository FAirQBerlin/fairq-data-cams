FROM python:3.10

RUN pip3 install pipenv

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    locales \
    libeccodes-dev \
    && sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && update-locale \
    && apt-get autoremove -y \
    && apt-get autoclean -y \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Europe/Berlin

WORKDIR /usr/src/app

COPY . ./

RUN set -ex && pipenv install --dev --deploy --system
