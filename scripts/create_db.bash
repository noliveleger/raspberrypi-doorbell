#!/bin/bash

PROJECT_DIR=/home/pi/doorbell/
DB_DIR="db"
if [[ ! -d "${PROJECT_DIR}${DB_DIR}" ]]; then
    mkdir -p "${PROJECT_DIR}${DB_DIR}"
    if [[ -f "${PROJECT_DIR}${DB_DIR}/app.db" ]]; then
        echo "Database already exists!"
        exit
    fi
    /home/pi/.local/bin/pipenv run pw_migrate migrate --database sqlite:///db/app.db
    exit  # exit virtualenv
fi

