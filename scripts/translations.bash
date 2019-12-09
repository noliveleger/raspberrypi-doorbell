#!/bin/bash

cd /home/pi/doorbell

if [[ ! -d locales ]]; then
    pybabel extract -k lazy_gettext -k ngettext:1,2 -o messages.pot -F babel.cfg .
    mkdir translations
    pybabel init -d locales -l fr -i messages.pot
    pybabel init -d locales -l en -i messages.pot
    mv messages.pot locales/
else
    pybabel extract -k lazy_gettext -k ngettext:1,2 -o locales/messages.pot -F babel.cfg .
    pybabel update -i locales/messages.pot -d locales
fi
