# coding: utf-8
import os
import logging

from werkzeug.utils import import_string


# config init
def load_config():

    root_path = os.path.realpath(os.path.normpath(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..',
        '..')
    ))

    environment_file = os.path.join(root_path, '.env')

    if not os.path.exists(environment_file):
        raise Exception('`.env` file is missing. Create one from `.env.sample`')

    environment = os.environ.get('FLASK_ENV', 'default')

    class_name = '{}Config'.format(environment.capitalize())
    config_class = import_string('app.config.{}.{}'.format(
        environment,
        class_name))()
    setattr(config_class, 'ROOT_PATH', root_path)

    return config_class


def get_logger(level_str):
    logging.basicConfig(format='[%(asctime)s] - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logger_ = logging.getLogger()
    if level_str == 'DEBUG':
        level = logging.DEBUG
    elif level_str == 'INFO':
        level = logging.INFO
    elif level_str == 'WARNING':
        level = logging.WARNING
    else:
        level = logging.ERROR
    logger_.setLevel(level)
    return logger_


config = load_config()
logger = get_logger(config.get('LOG_LEVEL'))
