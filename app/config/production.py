# -*- coding: utf-8 -*-
from .default import DefaultConfig


class ProdConfig(DefaultConfig):

    ENV = "prod"

    FSWEBCAM_RESOLUTION = '1280x720'
    FSWEBCAM_ROTATE = 180
