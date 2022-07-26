FROM python:3.8-slim-buster

COPY . /CodeAnalysis/
WORKDIR /CodeAnalysis/

CMD ["python3"]