# -*- coding: utf-8 -*-
import os


def load_config():
    """
    Returns the configuration class according to the PYTHON_ENV variable.
    :return: {Object}
    """
    environment = os.environ.get("PYTHON_ENV", "default")
    class_ = "{}{}".format(environment[0].upper(), environment[1:].lower())
    return import_string("app.config.{}Config".format(class_))

