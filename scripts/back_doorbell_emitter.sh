#!/bin/sh

# Used by `amazon-dash` service to make the chime rings
# Look at `/etc/amazon-dash.yml`

cd /home/pi/doorbell/
/home/pi/.local/bin/pipenv run python back_doorbell_emitter.py
