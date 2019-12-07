# coding: utf-8
from .default import DefaultConfig


class DevelopmentConfig(DefaultConfig):

    ENV = 'dev'

    LOG_LEVEL = 'DEBUG'
    WEBCAM_RESOLUTION = '1280x720'
