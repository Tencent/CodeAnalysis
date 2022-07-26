FROM python:3.7.12-slim

ARG EXTRA_TOOLS="curl wget python3-dev git git-lfs vim-tiny gcc locales subversion telnet procps"

RUN apt-get update \
    && apt-get install -y --no-install-recommends $EXTRA_TOOLS \
    && apt-get clean \
    && echo "LC_ALL=zh_CN.UTF-8" >> /etc/environment \
    && echo "zh_CN.UTF-8 UTF-8" > /etc/locale.gen \
    && echo "LANG=zh_CN.UTF-8" > /etc/locale.conf \
    && locale-gen \
    && ln -sf /usr/share/zoneinfo/Asia/Hong_Kong /etc/localtime \
    && rm -rf /var/cache/apt/* /root/.cache

WORKDIR /workspace/client

COPY . .

RUN pip3 install --no-cache-dir -r requirements/app_reqs.pip \
    && bash requirements/install.sh

CMD [ "python3", "codepuppy.py", "localscan"]