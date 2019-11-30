# -*- coding: utf-8 -*-
from .default import DefaultConfig


class DevelopmentConfig(DefaultConfig):

    LOG_LEVEL = 'DEBUG'

