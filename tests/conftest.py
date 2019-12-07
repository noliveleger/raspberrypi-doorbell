# coding: utf-8
import os
import pytest

from gpiozero import Device
from gpiozero.pins.mock import MockFactory

from app import create_app
from app.models import database, get_models

from app.config import config as config_


@pytest.yield_fixture()
def no_default_factory(request):
    save_pin_factory = Device.pin_factory
    Device.pin_factory = None
    yield None
    Device.pin_factory = save_pin_factory


@pytest.yield_fixture(scope='function')
def mock_factory(request):
    save_factory = Device.pin_factory
    Device.pin_factory = MockFactory()
    yield Device.pin_factory
    # This reset() may seem redundant given we're re-constructing the factory
    # for each function that requires it but MockFactory (via LocalFactory)
    # stores some info at the class level which reset() clears.
    if Device.pin_factory is not None:
        Device.pin_factory.reset()
    Device.pin_factory = save_factory


@pytest.fixture(scope='session')
def app():

    app = create_app()
    models = get_models()

    with app.app_context():
        database.create_tables(models)
        yield app
        database.drop_tables(models)

    os.unlink(config_.get('DATABASE').get('database'))


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()
