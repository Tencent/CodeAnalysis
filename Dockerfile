FROM python:3.7-slim-bullseye

ENV REDIS_PASSWD=tca2022
ENV MYSQL_PASSWORD=TCA!@#2021

ARG EXTRA_TOOLS="gnupg curl wget jq net-tools procps python3-dev default-libmysqlclient-dev locales inotify-tools gcc subversion git telnet iputils-ping vim openssh-client redis nginx unzip libsasl2-dev libldap2-dev libssl-dev"

# RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak && \
#     && echo 'deb http://mirrors.tencent.com/debian/ bullseye main non-free contrib' > /etc/apt/sources.list \
#     && echo 'deb http://mirrors.tencent.com/debian/ bullseye-updates main non-free contrib' >> /etc/apt/sources.list \
#     && echo 'deb http://mirrors.tencent.com/debian-security bullseye-security main non-free contrib' >> /etc/apt/sources.list \
#     && mkdir -p ~/.pip/ \
#     && echo "[global]\nindex-url = https://mirrors.cloud.tencent.com/pypi/simple\n[install]\ntrusted-host=mirrors.cloud.tencent.com" > ~/.pip/pip.conf

RUN set -ex && cd / \
    && apt-get update \
    && apt-get install -y --no-install-recommends $EXTRA_TOOLS \
    && wget -O /tmp/mariadb_repo_setup http://downloads.mariadb.com/MariaDB/mariadb_repo_setup \
    && chmod +x /tmp/mariadb_repo_setup \
    && bash /tmp/mariadb_repo_setup --mariadb-server-version="mariadb-10.6" \
    && apt-get install -y mariadb-server mariadb-backup \
    && apt-get clean \
    && echo "LC_ALL=zh_CN.UTF-8" >> /etc/environment \
    && echo "zh_CN.UTF-8 UTF-8" > /etc/locale.gen \
    && echo "LANG=zh_CN.UTF-8" > /etc/locale.conf \
    && locale-gen \
    && ln -sf /usr/share/zoneinfo/Asia/Hong_Kong /etc/localtime

RUN pip install -U setuptools pip \
    && pip install gunicorn==20.1.0 celery==5.2.3 supervisor==4.2.4 

COPY ./ /CodeAnalysis/
WORKDIR /CodeAnalysis/

EXPOSE 80 8000 9001

RUN chmod +x /CodeAnalysis/scripts/docker/init.sh \
    && chmod +x /CodeAnalysis/scripts/docker/start.sh \
    && bash /CodeAnalysis/scripts/docker/init.sh \
    && rm -rf /var/cache/apt/* /root/.cache

ENTRYPOINT ["./scripts/docker/start.sh"]
