# coding: utf-8
import os
import tempfile

from .default import DefaultConfig


class TestingConfig(DefaultConfig):

    TESTING = True
    DEBUG = True

    SERVER_NAME = 'testserver.localdomain'

    _, db_path = tempfile.mkstemp()

    DATABASE = {
        'database': db_path,
        'pragmas': (('journal_mode', 'wal'),
                    ('cache_size', -1024 * 64),
                    ('foreign_keys', 1))
    }

    WEBRTC_CALL_HEARTBEAT_INTERVAL = 2
    AUTH_DATETIME_PADDING = 2
    BUTTON_PRESS_THRESHOLD = 2
