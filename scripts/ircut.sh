#!/bin/sh

# Add this script to `cron.d`.
# For example to run every 30 seconds
# * * * * * pi /bin/sh /home/pi/doorbell/scripts/ircut.sh >> /var/log/ir_cut_off.log 2>&1
# * * * * * pi sleep 30 && /bin/sh /home/pi/doorbell/scripts/ircut.sh >> /var/log/ir_cut_off.log 2>&1
# Set `DAY_LIGHT_INTERVAL_CHECK` in config.ini to `30`

cd /home/pi/doorbell/
/home/pi/.local/bin/pipenv run python ircut.py
