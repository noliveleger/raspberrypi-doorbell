Why buy a Smart Doorbell when you can do it yourself with a Raspberry Pi.  
The concept is pretty simple. When the button is pressed, a notification is sent to your smart phone and the doorbell rings.

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Run it](#run-it)
4. [Issues](#issues)
5. [Miscellaneous](#miscellaneous) 
6. [ToDo](#todo) 

## Requirements

**Software:**

- [A Telegram API Token](./docs/telegram.md)

**Hardware:**

- RaspberryPi (Models 3 or 4 are recommended for motion detection and recordings. Mine is 3B+)
- Camera
- [Electronic components](./docs/electronic-components.md) to connect existing doorbell

If you want 2-ways communication, you also need:

- Speaker
- Microphone

After many tries/errors, I decided to use a [USB Camera](http://www.webcamerausb.com/elp-wide-angle-fisheye-lens-cmos-ov2710-night-vision-1080p-hd-webcam-usb-with-camera-support-ir-cut-p-233.html) instead of RPi Camera because:

- The USB cable is easier to bend than the ribbon of the RPi Camera
- You can find USB Cameras with microphone on-board. Easier to fit in the doorbell enclosure than an extra [USB microphone](https://www.adafruit.com/product/3367)

I also decided to use a [3.5 jack speaker](https://static.bhphoto.com/images/images1000x1000/1394551256_1031266.jpg) instead of USB speakers. I could not make the 2-ways communication work with the [USB speakers I had](https://www.adafruit.com/product/3369).


## Installation

- **Dependencies**

    ```
    pi@pi:~ $ sudo apt-get update
    pi@pi:~ $ sudo apt-get install python3-pip git vim
    pi@pi:~ $ sudo apt-get install build-essential libssl-dev libffi-dev python-dev
    pi@pi:~ $ sudo apt-get install python3-rpi.gpio
    pi@pi:~ $ pip3 install pipenv --user
    pi@pi:~ $ git clone https://github.com/noliveleger/raspberrypi-doorbell.git
    pi@pi:~ $ cd raspberrypi-doorbell
    pi@pi:~/raspberrypi-doorbell $ pipenv install
    ```
    
- **Motion detection and recordings**
    
    The project relies on `MotionEye` project. [Follow instructions](https://github.com/ccrisan/motioneye/wiki/Install-On-Raspbian).   
    If you want to activate hardware encoding, [read this](https://github.com/ccrisan/motioneye/issues/930).
    
    If you don't want to use `MotionEye`, do not forget to change `USE_MOTION` to `False` in `app/config/production.py`.  
    You will also need this other dependency: 
    
    ```
    pi@pi:~ $ sudo apt-get update && sudo apt-get install fswebcam
    ```
    _ToDo support RaspberryPi Cam and raspistill_

- **Create `.env` file**

    Copy `.env.sample` to `.env` and update settings to match your environment.
    
- **Change `production.py` file**

    Update `app/config/production.py` to match your production environment.

- **Create DB**

    ```
    pi@pi:~/raspberrypi-doorbell $ /bin/bash scripts/create_db.bash
    ```

- **Install web app** (Only needed if you want to use 2-ways communication)

    ```
    pi@pi:~/raspberrypi-doorbell $ sudo apt-get update
    pi@pi:~/raspberrypi-doorbell $ sudo apt-get install nginx
    ```
    
    For `Stretch`, https://stackoverflow.com/a/53366419
    
    Install NVM https://github.com/nvm-sh/nvm
    
    ```
    pi@pi:~/raspberrypi-doorbell $ nvm install node
    pi@pi:~/raspberrypi-doorbell $ cd app/www/mobile
    pi@pi:~/raspberrypi-doorbell/app/www/mobile $ npm install
    pi@pi:~/raspberrypi-doorbell/app/www/mobile $ npm run build
    ```
    
    [Follow these instructions](./docs/nginx.md) to setup NGINX as a reverse proxy for Flask with HTTPS.   
    

- **Install UV4L** (Only needed if you want to use 2-ways communication)


    This project relies on `UV4L` server to establish two-ways audio communication with WebRTC.  
    Please visit [https://www.linux-projects.org/uv4l/installation/](https://www.linux-projects.org/uv4l/installation/) for installation.  
    For `Buster` users, follow instructions for `Stretch` but also [these ones](https://www.raspberrypi.org/forums/viewtopic.php?t=247305). Stretch openssl.conf is available [here](/docs/openssl/openssl.cnf)
    
    If you are using an USB camera, please read [issues](#issues) section below.


## Run it

1. Daemon

    ```
    pi@pi:~/raspberrypi-doorbell $ pipenv shell
    (raspberrypi-doorbell) pi@pi:~/raspberrypi-doorbell $ flask commands daemon
    ```
    
    [Create a service](https://medium.com/@benmorel/creating-a-linux-service-with-systemd-611b5c8b91d6) to start at boot.
    
    ```
    [Unit]
    Description=DoorBell daemon
    After=network.target
    StartLimitIntervalSec=30
    [Service]
    WorkingDirectory=/home/pi/raspberrypi-doorbell
    Environment="PATH=/home/pi/.local/bin:/home/pi/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:"
    # Uncomment the line below if you want to use `uv4l_uvc` driver.
    # Environment="LD_PRELOAD=/usr/lib/uv4l/uv4lext/armv6l/libuv4lext.so"
    Type=simple
    Restart=on-failure
    RestartSec=1
    User=pi
    ExecStart=/home/pi/.local/bin/pipenv run flask commands daemon
        
    [Install]
    WantedBy=multi-user.target
    ```
    
2. Web App    

    ```
    pi@pi:~/raspberrypi-doorbell $ pipenv shell
    (raspberrypi-doorbell) pi@pi:~/raspberrypi-doorbell $ flask run
    ```
    
    [Create a service](https://medium.com/@benmorel/creating-a-linux-service-with-systemd-611b5c8b91d6) to start at boot.
    
    ```
    [Unit]
    Description=DoorBell Web App
    After=network.target
    StartLimitIntervalSec=30
    [Service]
    WorkingDirectory=/home/pi/raspberrypi-doorbell
    Environment="PATH=/home/pi/.local/bin:/home/pi/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:"
    Type=simple
    Restart=on-failure
    RestartSec=1
    User=pi
    ExecStart=/home/pi/.local/bin/pipenv run flask run
        
    [Install]
    WantedBy=multi-user.target
    ```


## Issues

This list is based on issues I faced.


- Almost no image controls with `uv4l-uvc` driver.

> Solved by [using `uvcvideo` driver](#using-uvc-video-driver)

- It often crashed when streaming with `uv4l-uvc`. Raspberry Pi needs to be restarted, USB port needs to be power cycled or restart driver 

> Solved by using [using `uvcvideo` driver](#using-uvc-video-driver)

- Picture became B&W after few hours IR Cut-Off was off. I needed to power recycle USB port or restart driver

> Solved by using [using `uvcvideo` driver](#using-uvc-video-driver) 

B&W picture still occur sometime with `uvc_video` driver but a lot less

- USB Camera with night vision does not return to day mode

> Solved by using a [home-made circuit controlled by GPIO](./docs/electronic-components.md#control-ir-cut-off-filter-with-gpio)

- The light sensor is not enough sensible and cannot be trigger manually. 

The light sensor that comes with the IR-LEDs board cannot be adjusted. I need to find a way to either switch the IR LEDs on programmatically (and to bypass the sensor) or try to put a tinted plastic film on the sensor to make it more sensible.

#### Using `uvcvideo` driver

- Remove `uvcvideo` from `modprobe` blacklist.  

  Comment out `blacklist uvcvideo` in `/etc/modprobe.d/uvcvideo-blacklist.conf`
- Tell `uv4l-uvc` to use external driver
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

## Miscellaneous

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

_TO-DO Complete documentation_



#### Using Amazon Dash Button as a back doorbell
Thanks to [Amazon Dash service](https://github.com/Nekmo/amazon-dash ""). 
It triggers a signal to the daemon which make the bell rings twice (instead once at front-door)

_TO-DO Complete documentation_


## ToDo

- Complete documentation 
    1. nginx
    2. uv4l configuration
    3. readme
    4. development
- Secure websocket
- Finish HTML templates for 404, 403 and 423 errors
