#!/bin/sh

#echo "[ $(date) ] Stopping streamer..."
#sudo systemctl stop streamer.service
echo "[ $(date) ] Stopping USB camera driver..."
sudo systemctl stop uv4l_uvc@05a3:9422.service
echo "[ $(date) ] Power cycling USB camera..."
sudo uhubctl -a off -p 3 -l 1-1
sleep 1
sudo uhubctl -a on -p 3 -l 1-1
sleep 1
echo "[ $(date) ] Starting USB camera driver..."
sudo systemctl start uv4l_uvc@05a3:9422.service
sleep 1
#echo "[ $(date) ] Starting streamer..."
#sudo systemctl start streamer.service
echo "[ $(date) ] Done"
