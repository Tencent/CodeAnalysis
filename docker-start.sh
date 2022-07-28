#!/usr/bin/env bash

case $1 in
  -h|--help)
    echo $'usage: docker-start\n\nStarts Docker (Docker.app) on macOS and waits until the Docker environment is initialized.'
    exit 0
    ;;
esac
(( $# )) && { echo "ARGUMENT ERROR: Unexpected argument(s) specified. Use -h for help." >&2; exit 2; }

[[ $(uname) == 'Darwin' ]] || { echo "This function only runs on macOS." >&2; exit 2; }

echo "-- Starting Docker.app, if necessary..."

open -g -a Docker.app || exit

# Wait for the server to start up, if applicable.  
i=0
while ! docker system info &>/dev/null; do
  (( i++ == 0 )) && printf %s '-- Waiting for Docker to finish starting up...' || printf '.'
  sleep 1
done
(( i )) && printf '\n'

echo "-- Docker is ready."
