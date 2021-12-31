FROM python:3.7.3
RUN apt-get update && apt-get install -y git subversion python-svn python-dev gcc svn-workbench mysql-client
#RUN echo "export LANG=\"en_US.UTF-8\"" >> /etc/profile && source /etc/profile && echo $LANG

RUN mkdir -p /var/www/django/codedog && cd /var/www/django/codedog

WORKDIR /var/www/django/codedog

COPY ./ ./

RUN pip install -U setuptools && pip install -r requirements.txt