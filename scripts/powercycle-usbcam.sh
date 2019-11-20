#!/bin/sh

DEVICE_ID=05a3:9422

echo "[ $(date) ] Stopping USB camera driver..."
sudo systemctl stop uv4l_uvc@${DEVICE_ID}.service
echo "[ $(date) ] Power cycling USB camera..."
sudo uhubctl -a off -p 3 -l 1-1
sleep 1
sudo uhubctl -a on -p 3 -l 1-1
sleep 1
echo "[ $(date) ] Starting USB camera driver..."
sudo systemctl start uv4l_uvc@${DEVICE_ID}.service
sleep 1
echo "[ $(date) ] Done"
