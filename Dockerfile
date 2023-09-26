FROM python:3.9

RUN pip3 install pipenv

RUN apt-get update && \
    apt-get -y install locales && \
    apt-get -y install libeccodes-dev && \
    sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale

ENV TZ=Europe/Berlin

WORKDIR /usr/src/app

COPY . ./

RUN set -ex && pipenv install --dev --deploy --system
