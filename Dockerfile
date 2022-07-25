FROM centos:centos7

ENV REDIS_PASSWD=tca2022
ENV MYSQL_PASSWORD=TCA!@#2021

ARG EXTRA_TOOLS="wget zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make libffi-devel xz-devel unzip git subversion"

RUN set -ex && cd / \
    && yum install -y $EXTRA_TOOLS \
    && yum install -y epel-release \
    && yum install -y redis nginx \
    && echo "LC_ALL=zh_CN.UTF-8" >> /etc/profile \
    && echo "LC_ALL=zh_CN.UTF-8" >> /etc/environment \
    && echo "zh_CN.UTF-8 UTF-8" > /etc/locale.gen \
    && echo "LANG=zh_CN.UTF-8" > /etc/locale.conf \
    && wget http://downloads.mariadb.com/MariaDB/mariadb_repo_setup \
    && chmod +x mariadb_repo_setup && ./mariadb_repo_setup --mariadb-server-version="mariadb-10.6" \
    && yum install -y MariaDB-server MariaDB-backup \
    && yum clean all

RUN wget "https://www.python.org/ftp/python/3.7.12/Python-3.7.12.tgz" \
    && tar zvxf Python-3.7.12.tgz -C /usr/local/src \
    && rm Python-3.7.12.tgz && cd /usr/local/src/Python-3.7.12 \
    && ./configure prefix=/usr/local/python3 --enable-shared \
    && make -j8 && make install && make clean \
    && ln -s /usr/local/python3/bin/python3 /usr/local/bin/python \
    && ln -s /usr/local/python3/bin/python3 /usr/local/bin/python3 \
    && ln -s /usr/local/python3/bin/pip3 /usr/local/bin/pip \
    && ln -s /usr/local/python3/bin/pip3 /usr/local/bin/pip3 \
    && ln -s /usr/local/python3/lib/libpython3.7m.so.1.0 /usr/lib/libpython3.7m.so.1.0 \
    && ldconfig && mkdir -p ~/.pip/ \
    && echo "[global]\nindex-url = https://mirrors.cloud.tencent.com/pypi/simple\n[install]\ntrusted-host=mirrors.cloud.tencent.com" > ~/.pip/pip.conf \
    && pip install gunicorn==20.1.0 celery==5.2.2 supervisor==4.2.4\
    && ln -s /usr/local/python3/bin/gunicorn /usr/local/bin/gunicorn \
    && ln -s /usr/local/python3/bin/celery /usr/local/bin/celery \
    && ln -s /usr/local/python3/bin/supervisord /usr/local/bin/supervisord \
    && ln -s /usr/local/python3/bin/supervisorctl /usr/local/bin/supervisorctl

COPY ./ /CodeAnalysis/
WORKDIR /CodeAnalysis/

EXPOSE 80 8000 9001

RUN chmod +x /CodeAnalysis/scripts/docker/init.sh \
    && chmod +x /CodeAnalysis/scripts/docker/start.sh \
    && bash /CodeAnalysis/scripts/docker/init.sh

ENTRYPOINT ["./scripts/docker/start.sh"]
