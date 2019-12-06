# -*- coding: utf-8 -*-
import os


class DefaultConfig:

    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')

    LOG_LEVEL = 'INFO'

    # telegram settings
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    TELEGRAM_CHAT_URL = os.getenv('TELEGRAM_CHAT_URL')

    # notification message
    NOTIFICATION_FRONT_DOOR_MESSAGE = "Quelqu'un est à la porte d'entrée"
    NOTIFICATION_BACK_DOOR_MESSAGE = "Quelqu'un est à la grille arrière"

    # fswebcam settings (useless if MotionEye is enabled)
    WEBCAM_BIN = '/usr/bin/fswebcam'
    WEBCAM_DEVICE = '/dev/video0'
    WEBCAM_RESOLUTION = '1920x1080'
    WEBCAM_DELAY = 2
    WEBCAM_ROTATE = 0
    WEBCAM_JPG_COMP = 90

    # Pins numbers in BCM mode
    LED_GPIO_BCM = 21
    BUTTON_GPIO_BCM = 20
    CHIME_GPIO_BCM = 19
    IR_CUTOFF_FORWARD_GPIO_BCM = 24
    IR_CUTOFF_BACKWARD_GPIO_BCM = 25
    IR_CUTOFF_ENABLER_GPIO_BCM = 23

    # Number of seconds before button can be pressed again
    BUTTON_PRESS_THRESHOLD = 5
    # Keep the led turned on during the day
    BUTTON_LED_ALWAYS_ON = False

    # Location of the doorbell. To calculate sunset/sunrise.
    ASTRA_CITY = 'Montreal'
    # Day Light offset (after sunset, before sunrise). In minutes.
    DAY_LIGHT_OFFSET = 15

    # Message Broker
    MESSAGE_BROKER_PORT = 65432
    MESSAGE_BROKER_HOST = '127.0.0.1'
    MESSAGE_BROKER_KEY = os.getenv('MESSAGE_BROKER_KEY', 'Change me!')

    # Amazon Dash button as Backdoor
    BACK_DOORBELL_DEVICE_MAC = os.getenv('BACK_DOORBELL_DEVICE_MAC')
    BACK_DOORBELL_RINGS_NUMBER = 2

    # MotionEye
    USE_MOTION = True
    MOTION_EYE_SNAPSHOT_URL = os.getenv('MOTION_EYE_SNAPSHOT_URL',
                                        'http://127.0.0.1:8765/picture/1/current/')

    TESTING = False

    # Flask App
    DATABASE = {
        'database': os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'db',
            'app.db'),
        'pragmas': (('journal_mode', 'wal'),
                    ('cache_size', -1024 * 64),
                    ('foreign_keys', 1))
    }

    AUTH_DATETIME_PADDING = 60

    WEB_APP_DOMAIN_NAME = os.getenv('WEB_APP_DOMAIN_NAME')
    WEB_APP_PORT = 443
    WEBRTC_WEBSOCKETS_PORT = 8090  # Default for UV4L UVC Server
    WEBRTC_ENDPOINT = '/stream/webrtc'  # Default for UV4L WebRTC server
    WEBRTC_ICE_SERVERS = {
        'iceServers': [{
            'urls': [
                'stun:stun.l.google.com:19302',
                'stun:{}:3478'.format(WEB_APP_DOMAIN_NAME)
            ]
        }]
    }

    # Interval in seconds, client call must tell server it's still alive.
    WEBRTC_CALL_HEARTBEAT_INTERVAL = 20

    """
    Available resolutions and frame rates at the min., max. and start configured 
    bitrates for adaptive streaming which will be scaled from the base 720p 30fps
    5 -> 320x240 15 fps
    10 -> 320x240 30 fps 
    20 -> 352x288 30 fps 
    25 -> 640x480 15 fps 
    30 -> 640x480 30 fps 
    35 -> 800x480 30 fps 
    40 -> 960x720 30 fps 
    50 -> 1024x768 30 fps 
    55 -> 1280x720 15 fps 
    60 -> 1280x720 30 fps (kbps min.800 max.4000 start 1200) 
    63 -> 1280x720 60 fps 
    65 -> 1280x768 15 fps 
    70 -> 1280x768 30 fps 
    75 -> 1536x768 30 fps 
    80 -> 1280x960 30 fps 
    90 -> 1600x768 30 fps 
    95 -> 1640x1232 15 fps 
    97 -> 1640x1232 30 fps 
    98 -> 1792x896 15 fps 
    99 -> 1792x896 30 fps 
    100 -> 1920x1080 15 fps 
    105 -> 1920x1080 30 fps 
    """
    WEBRTC_VIDEO_FORMAT = 60

    """
    When `True`, `WEBRTC_VIDEO_FORMAT` is applied and video is at full resolution,
    otherwise it stays at 640x480.
    
    2019-11-30 
    Worked with: 
        - iOS 13, Safari
        - mac OS 10.15, Safari
        - mac OS 10.15, Firefox 70.0.1 
    Failed with:
        - iOS 13, Chrome
        - iOS 13, Firefox
        - iOS 13, Opera
        - macOS 10.15, Chrome 78
    """
    WEBRTC_FORCE_HW_VCODEC = False

    CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'img-src': [
            "'self'",
            'data:'
        ],
        'style-src': "'self'",
        'script-src': "'self'",
        'connect-src': [
            "'self'",
            'wss://{}:{}{}'.format(
                WEB_APP_DOMAIN_NAME,
                WEBRTC_WEBSOCKETS_PORT,
                WEBRTC_ENDPOINT
            )
        ]
    }

    # Cron job interval check (whether it's day or not). In seconds.
    # Each class must implement a `cron` method.
    CRON_TASKS = [
        ('app.models.call.Call', WEBRTC_CALL_HEARTBEAT_INTERVAL),
        ('app.devices.button.Button', 60),
        ('app.devices.ir_cut_off.IRCutOff', 60)
    ]

    @property
    def env(self):
        return self.get('ENV')

    @classmethod
    def get(cls, attribute, default=None):
        return getattr(cls, attribute, default)
