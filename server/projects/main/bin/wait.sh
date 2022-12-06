#!/bin/bash

function wait_for_service(){
  SERVICE=${1/:/' '}
  until nc -vz $SERVICE > /dev/null; do
    >&2 echo "$SERVICE is unavailable - sleeping"
    sleep 2
  done
  >&2 echo "$SERVICE is up"
}

function wait_for() {
  for service in "$@"
  do
    wait_for_service $service
  done
}

wait_for "$@"