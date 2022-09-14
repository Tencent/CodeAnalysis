#!/bin/bash

function error_exit() {
    LOG_ERROR "$1" 1>&2
    exit 1
}

python manage.py migrate --noinput --traceback || error_exit "migrate table failed"