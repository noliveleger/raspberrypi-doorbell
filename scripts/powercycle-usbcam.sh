#!/bin/sh

echo "Power cycling USB camera..."
sudo uhubctl -a off -p 3 -l 1-1
sleep 1
sudo uhubctl -a on -p 3 -l 1-1
sleep 1
echo "Restarting USB camera driver..."
sudo systemctl restart uv4l_uvc@05a3:9422.service
echo "Done"
