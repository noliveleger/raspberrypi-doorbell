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

    # fswebcam settings
    FSWEBCAM_BIN = '/usr/bin/fswebcam'
    FSWEBCAM_DEVICE = '/dev/video0'
    FSWEBCAM_RESOLUTION = '1920x1080'
    FSWEBCAM_DELAY = 2
    FSWEBCAM_ROTATE = 0
    FSWEBCAM_JPG_COMP = 90

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
    # Cron job interval check (whether it's day or not). In seconds.
    DAY_LIGHT_INTERVAL_CHECK = 30

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

    WEBRTC_HOST = os.getenv('WEBRTC_HOST')

    @property
    def env(self):
        return self.get('ENV')

    @classmethod
    def get(cls, attribute, default=None):
        return getattr(cls, attribute, default)
