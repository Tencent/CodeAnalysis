FROM python:3.7-slim-bullseye

ARG EXTRA_TOOLS="gnupg curl wget jq net-tools procps default-libmysqlclient-dev locales inotify-tools gcc telnet iputils-ping vim openssh-client libsasl2-dev libldap2-dev libssl-dev"

RUN set -ex && cd / \
    && apt-get update \
    && apt-get install -y --no-install-recommends $EXTRA_TOOLS \
    && apt-get update \
    && apt-get install -y mariadb-client \
    && apt-get clean \
    && echo "LC_ALL=zh_CN.UTF-8" >> /etc/environment \
    && echo "zh_CN.UTF-8 UTF-8" > /etc/locale.gen \
    && echo "LANG=zh_CN.UTF-8" > /etc/locale.conf \
    && locale-gen \
    && ln -sf /usr/share/zoneinfo/Asia/Hong_Kong /etc/localtime \
    && rm -rf /var/cache/apt/* /root/.cache

WORKDIR /var/www/django/codedog

COPY . .

RUN mkdir -p log/ && \
    pip install -U setuptools pip && \
    pip install -r requirements.txt
