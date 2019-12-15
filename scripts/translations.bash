#!/bin/bash

BASEDIR="$(dirname $(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd))"
cd $BASEDIR

VENV_COMMAND=""

if [[ "$FLASK_ENV" == "" ]]; then
    VENV_COMMAND="pipenv run "
fi

if [[ ! -d locales ]]; then
    $VENV_COMMAND pybabel extract -k lazy_gettext -k ngettext:1,2 -o messages.pot -F babel.cfg .
    mkdir translations
    $VENV_COMMAND pybabel init -d locales -l fr -i messages.pot
    $VENV_COMMAND pybabel init -d locales -l en -i messages.pot
    mv messages.pot locales/
else
    $VENV_COMMAND pybabel extract -k lazy_gettext -k ngettext:1,2 -o locales/messages.pot -F babel.cfg .
    $VENV_COMMAND pybabel update -i locales/messages.pot -d locales
fi
