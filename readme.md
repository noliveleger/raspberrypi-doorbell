## Introduction
Why buy a Nest Hello or Amazon Ring when you can do it yourself with a Raspberry Pi.  
The idea is pretty simple. When the button is pressed, a notification is sent to [Telegram](https://telegram.org/) and the doorbell rings. 

**Software:**

- A Telegram API Token

**Hardware:**

- RaspberryPi (I use the 3B+ model on Raspbian Stretch)
- Camera
- [Electronic components](#) to connect existing doorbell


If you want 2-ways communication (not implemented yet), you also need:

- Speaker
- Microphone

After many tries/errors, I decided to use a [USB Camera](http://www.webcamerausb.com/elp-wide-angle-fisheye-lens-cmos-ov2710-night-vision-1080p-hd-webcam-usb-with-camera-support-ir-cut-p-233.html) instead of RPi Camera because:

- The USB cable is easier to bend than the ribbon of the RPi Camera
- You can find USB Cameras with microphone on-board. Easier to fit in the doorbell enclosure than an extra [USB microphone](https://www.adafruit.com/product/3367)

However, I faced some issues [See below](#usb-camera-issues).

I also decided to use a [3.5 jack speaker](https://static.bhphoto.com/images/images1000x1000/1394551256_1031266.jpg) instead of USB speakers. I could not make the 2-ways communication work with the [USB speakers I have](https://www.adafruit.com/product/3369).

 

## Installation

#### Dependencies:

```
pi@pi:~ $ sudo apt-get update
pi@pi:~ $ sudo apt-get install python3-pip git vim
pi@pi:~ $ sudo apt-get install build-essential libssl-dev libffi-dev python-dev
pi@pi:~ $ sudo apt-get install python3-rpi.gpio
pi@pi:~ $ sudo apt-get install nodejs
pi@pi:~ $ pip3 install pipenv --user
pi@pi:~ $ git clone https://oleger@bitbucket.org/oleger/doorbell.git
pi@pi:~ $ cd doorbell
pi@pi:~/doorbell $ pipenv install
```

1. Create DB
`pi@pi:~/doorbell $ /bin/bash scripts/create_db.bash`

2. Build static files
```
pi@pi:~/doorbell $ cd app/www/mobile
pi@pi:~/doorbell/app/www/mobile $ npm install
pi@pi:~/doorbell/app/www/mobile $ npm run build
```




#### UV4L:

This project relies on `uv4l` project to establish two-ways audio communication with webrtc.

Please follow, https://www.linux-projects.org/uv4l/installation/

If you use an USB camera, please read [issues](todo-link "") section below

Buster and SSL: https://www.raspberrypi.org/forums/viewtopic.php?t=247305

TO-DO: 

- Use NGINX and Flask App to expose a mobile web app.  
- Complete documentation



#### Get Telegram Token and Chat room info

TO-DO Completed documenation

#### Create `DoorBell` service with `systemctl`
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
    

## Issues

- Almost no image controls with `uv4l-uvc` driver.

> Solved by [using `uvcvideo` driver](#)

- It often crashed when streaming with `uv4l-uvc`. I needed to power recycle USB port or restart driver. 

> Solved by using [using `uvcvideo` driver](#)

- Picture became B&W after few hours IR Cut-Off was off. I needed to power recycle USB port or restart driver.

> Solved by using [using `uvcvideo` driver](#)

- USB Camera with night vision does not return to day mode

> Solved by using a [home-made circuit controlled by GPIO](#)

- The light sensor is not enough sensible and cannot be trigger manually



#### Using `uvcvideo` driver

- Remove `uvcvideo` from `modprobe` blacklist.  

  Comment out `blacklist uvcvideo` in `/etc/modprobe.d/uvcvideo-blacklist.conf`
- Tell `uv4l-uvc` to use external driver (optional if you do not want to use the two-ways communication)
    1. Edit `/etc/init.d/uv4l_uvc`, replace `driver=uvc` with `--external-driver=yes`    
    **Before:**  
    `$UV4L -k --sched-rr --mem-lock --config-file=$CONFIGFILE --external-driver=yes --driver-config-file=$CONFIGFILE --server-option=--editable-config-file=$CONFIGFILE --device-id $2`  
    **After:**  
    `$UV4L -k --sched-rr --mem-lock --config-file=$CONFIGFILE --external-driver=yes --driver-config-file=$CONFIGFILE --server-option=--editable-config-file=$CONFIGFILE --device-id $2`  
    2. Edit `/etc/uv4l/uv4l-uvc.conf`, replace  
    
    ```
    driver = uvc  
    video_nr = 0
    auto-video_nr = yes
    ```
    with
    
    ```
    # driver = uvc  
    # video_nr = 0
    # auto-video_nr = yes
    external-driver = yes
    device-name = video0
    ```

#### Control IR Cut-off filter with GPIO

I decided to by-pass the control of the IR Cut-Off by using this circuit

![IR Cut-Off diagram](./docs/ir-cut-off.svg)

The IR Cut-off is switched on/off at sunset/sunrise hours. It can set in [config.ini](https://bitbucket.org/oleger/doorbell/src/93265682e4dc60b9be271103960558cad6c4f83a/config.ini.sample#lines-30:35)

#### Power Cycle USB Camera

One of the workaround is to power cycle USB port to avoid rebooting the RaspberryPI.
Thanks to this utility: [uhubctl](https://github.com/mvp/uhubctl ""), it is possible.

Usage:

```
$> sudo uhubctl -a <action> -p <port_number> -l <hub_location>
```

On RaspberryPI 3B+ and USB Port 3

```
$> sudo uhubctl -a off -p 3 -l 1-1
```

[A script](scripts/powercycle-usbcam.sh) is available to call it. Please adapt it to your settings.



## Electronic components

TO-DO Complete documentation

## Amazon Dash Button
Thanks to [Amazon Dash service](https://github.com/Nekmo/amazon-dash ""). 
It triggers a signal to the daemon which make the bell rings twice (instead once at front-door)

TO-DO Complete documentation

## Motion
```
pi@pi:~ $ sudo apt-get update
pi@pi:~ $ sudo apt-get install autotools-dev libltdl-dev libtool autoconf autopoint
```
TO-DO Complete documentation


## DB

```
pw_migrate migrate --database sqlite:///db/app.db
```
TO-DO Complete documentation


