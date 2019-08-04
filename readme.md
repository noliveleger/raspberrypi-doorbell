## Installation

```
pi@pi:~ $ sudo apt-get update
pi@pi:~ $ sudo apt-get install python3-pip git vim
pi@pi:~ $ sudo apt-get install build-essential libssl-dev libffi-dev python-dev
pi@pi:~ $ sudo apt-get install python-rpi.gpio python3-rpi.gpio
pi@pi:~ $ pip install pipenv --user
pi@pi:~ $ git clone https://oleger@bitbucket.org/oleger/doorbell.git
pi@pi:~ $ cd doorbell
pi@pi:~/doorbell $ pipenv install

``` 

### UV4L
TO-DO 


## Create a telegram bot

TO-DO

## Create Linux service with `systemctl`
From this [tutorial](https://medium.com/@benmorel/creating-a-linux-service-with-systemd-611b5c8b91d6 "")

```
[Unit]
Description=DoorBell daemon
After=network.target
StartLimitIntervalSec=30
[Service]
WorkingDirectory=/home/pi/doorbell
Environment="PATH=/home/pi/.local/bin:/home/pi/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:"
Environment="LD_PRELOAD=/usr/lib/uv4l/uv4lext/armv6l/libuv4lext.so"
Type=simple
Restart=on-failure
RestartSec=1
User=pi
ExecStart=/home/pi/.local/bin/pipenv run python daemon.py

[Install]
WantedBy=multi-user.target
```



## Power Cycle USB Camera

USB Camera with night vision does not return to day mode.
Workaround is to power cycle USB port thanks to this utility: [uhubctl](https://github.com/mvp/uhubctl "")

Usage:
```
$> sudo uhubctl -a <action> -p <port_number> -l <hub_location>
```

On RaspberryPI 3B+ and USB Port 3
```
sudo uhubctl -a off -p 3 -l 1-1
```

`uv4l_uvc` driver needs to be restart too.
```
sudo systemctl restart uv4l_uvc@05a3:9422.service
```


