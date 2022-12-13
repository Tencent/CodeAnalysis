#!/bin/bash

function error_exit() {
    echo "$1" 1>&2
    exit 1
}

python manage.py createcachetable >/dev/null || error_exit "create cache table failed"
python manage.py migrate --noinput --traceback >/dev/null || error_exit "migrate table failed"
python manage.py initializedb_open || error_exit "init project data failed"
python manage.py initialize_exclude_paths || error_exit "init project exclude path data failed"
python manage.py loadlibs all --dirname open_source_toollib --ignore-auth || error_exit "load tool libs data failed"
python manage.py loadcheckers all --dirname open_source || error_exit "load tool checkers data failed"
python manage.py loadpackages all --dirname open_source_package || error_exit "load tool checkpackages data failed"