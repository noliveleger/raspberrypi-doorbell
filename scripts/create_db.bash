#!/bin/bash

BASEDIR="$(dirname $(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd))"
cd $BASEDIR

DB_DIR="db"
if [[ ! -d "${BASEDIR}/${DB_DIR}" ]]; then
    mkdir -p "${BASEDIR}/${DB_DIR}"
    if [[ -f "${BASEDIR}/${DB_DIR}/app.db" ]]; then
        echo "Database already exists!"
        exit
    fi

    if [[ "$FLASK_ENV" == "" ]]; then
        /home/pi/.local/bin/pipenv run pw_migrate migrate --database sqlite:///db/app.db
    else
        pw_migrate migrate --database sqlite:///db/app.db
    fi

fi

