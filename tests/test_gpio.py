# coding: utf-8
import time

from mock import patch

from app.config import config
from app.devices.button import Button
from app.helpers.sundial import Sundial
from app.devices.ir_cut_off import IRCutOff
from . import (
    DummyThread,
    MockSocket,
)


@patch('socket.socket', new=MockSocket)
@patch('app.threads.chime.Chime.run', new=DummyThread.run)
@patch('app.threads.camera.Camera.run', new=DummyThread.run)
@patch('app.threads.notification.Notification.run', new=DummyThread.run)
def test_button(mock_factory):

    led_pin = mock_factory.pin(config.get('LED_GPIO_BCM'))
    button_pin = mock_factory.pin(config.get('BUTTON_GPIO_BCM'))

    button = Button()
    button.activate_led()

    button._led_always_on = True  # Force LED to be on
    checkpoint = button.last_pressed
    button_pin.drive_low()  # button is pressed
    assert not led_pin.state
    assert led_pin.state == button.led.is_lit
    assert checkpoint == button.last_pressed  # Do not ring. Pressed too fast
    time.sleep(0.1)
    button_pin.drive_high()  # button is released
    assert led_pin.state
    assert led_pin.state == button.led.is_lit

    # Wait for threshold to expire
    button._led_always_on = False  # Force LED to be on during the day
    time.sleep(int(config.get('BUTTON_PRESS_THRESHOLD', 1)))
    button_pin.drive_low()  # button is pressed
    should_be_lit = not Sundial().is_day()
    assert led_pin.state is not should_be_lit
    time.sleep(0.1)
    assert checkpoint != button.last_pressed
    button_pin.drive_high()  # button is released
    assert led_pin.state is should_be_lit


def test_ir_cut_off(mock_factory):

    forward_pin = mock_factory.pin(config.get('IR_CUTOFF_FORWARD_GPIO_BCM'))
    backward_pin = mock_factory.pin(config.get('IR_CUTOFF_BACKWARD_GPIO_BCM'))
    enabler_pin = mock_factory.pin(config.get('IR_CUTOFF_ENABLER_GPIO_BCM'))

    ir_cut_off = IRCutOff()
    # Toggle in DAY mode
    ir_cut_off._toggle(Sundial.DAY)
    assert not forward_pin.state
    assert backward_pin.state
    assert enabler_pin.state

    # Idle
    ir_cut_off.stop()
    assert not forward_pin.state
    assert not backward_pin.state
    assert not enabler_pin.state

    # Toggle Night mode
    ir_cut_off._toggle(Sundial.NIGHT)
    assert forward_pin.state
    assert not backward_pin.state
    assert enabler_pin.state
    ir_cut_off.stop()
