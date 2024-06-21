FROM python:3.7-slim-bullseye

ARG EXTRA_TOOLS="curl wget python3-dev git git-lfs vim-tiny gcc locales subversion telnet procps openssh-client libreadline-dev"

RUN apt-get update \
    && apt-get install -y --no-install-recommends $EXTRA_TOOLS \
    && apt-get clean \
    && echo "LC_ALL=zh_CN.UTF-8" >> /etc/environment \
    && echo "zh_CN.UTF-8 UTF-8" > /etc/locale.gen \
    && echo "LANG=zh_CN.UTF-8" > /etc/locale.conf \
    && locale-gen \
    && ln -sf /usr/share/zoneinfo/Asia/Hong_Kong /etc/localtime \
    && rm -rf /var/cache/apt/* /root/.cache

ARG TARGETARCH
RUN if [ "$TARGETARCH" = "amd64" ]; then \
      cd /lib/x86_64-linux-gnu && ln -sf libreadline.so.8.1 libreadline.so.6; \
    elif [ "$TARGETARCH" = "arm64" ]; then \
      cd /lib/aarch64-linux-gnu && ln -sf libreadline.so.8.1 libreadline.so.6; \
    fi && \
    echo "TARGETARCH is $TARGETARCH"

WORKDIR /workspace/client

COPY requirements requirements

RUN pip3 install --no-cache-dir -U pip \
    && pip3 install --no-cache-dir -r requirements/app_reqs.pip \
    && bash requirements/install.sh

COPY . .

# 避免挂载的代码目录owner不是root时，导致git blame异常 - fatal: unsafe repository ('/xxx/xxx' is owned by someone else)
RUN git config --global --add safe.directory '*'

CMD [ "python3", "codepuppy.py", "localscan"]
