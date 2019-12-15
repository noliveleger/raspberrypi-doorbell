#!/bin/sh

# Used by `amazon-dash` service to make the chime rings
# Look at `/etc/amazon-dash.yml`

BASEDIR="$(dirname $(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd))"
cd $BASEDIR

if [[ "$FLASK_ENV" == "" ]]; then
    /home/pi/.local/bin/pipenv run flask commands back-doorbell-emitter
else
    flask commands back-doorbell-emitter
fi
