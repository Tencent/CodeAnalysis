#!/bin/bash

function error_exit() {
    echo "$1" 1>&2
    exit 1
}

python manage.py createcachetable >/dev/null || error_exit "create cache table failed"
python manage.py migrate --noinput --traceback >/dev/null || error_exit "migrate table failed"
python manage.py initializedb || error_exit "init project data failed"