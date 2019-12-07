# coding: utf-8
from .default import DefaultConfig


class ProdConfig(DefaultConfig):

    ENV = 'prod'

    WEBCAM_RESOLUTION = '1280x720'
    WEBCAM_ROTATE = 180

    WEBRTC_FORCE_HW_VCODEC = True
