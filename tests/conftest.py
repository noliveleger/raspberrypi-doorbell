# -*- code utf-8 -*-
# Simplified version of gpiozero conftest.py

import os
import pytest

from gpiozero import Device
from gpiozero.pins.mock import MockFactory, MockPWMPin


def pytest_configure(config):
    os.environ['FLASK_ENV'] = 'testing'
    return config


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
