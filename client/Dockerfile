FROM python:3.7.12-slim

ARG EXTRA_TOOLS="curl wget python3-dev git git-lfs vim"

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends $EXTRA_TOOLS

COPY ./requirements ./requirements

RUN pip3 install --no-cache-dir -r requirements/app_reqs.pip

RUN bash requirements/install.sh

WORKDIR /workspace/client
CMD [ "python3", "codepuppy.py", "localscan"]