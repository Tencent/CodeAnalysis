FROM python:3.7.12-slim
# For ARM
# FROM arm64v8/python:3.7.12-slim

RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak && \
    echo 'deb http://mirrors.tencent.com/debian/ bullseye main non-free contrib' > /etc/apt/sources.list && \
    echo 'deb http://mirrors.tencent.com/debian/ bullseye-updates main non-free contrib' >> /etc/apt/sources.list && \
    echo 'deb http://mirrors.tencent.com/debian-security bullseye-security main non-free contrib' >> /etc/apt/sources.list

ARG EXTRA_TOOLS="gnupg curl wget jq net-tools procps default-libmysqlclient-dev locales inotify-tools gcc telnet iputils-ping vim openssh-client"

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
    mkdir ~/.pip/ && echo "[global]\nindex-url = https://mirrors.cloud.tencent.com/pypi/simple" >> ~/.pip/pip.conf && \
    pip install -U setuptools pip && \
    pip install -r requirements.txt