# -*- code utf-8 -*-
import time

from mock import patch

from helpers.config import config
from helpers.button import Button
from helpers.sundial import Sundial
from helpers.ir_cutoff import IRCutOff


class DummyThread:

    def run(self):
        return


@patch('threads.chime.Chime.run', new=DummyThread.run)
@patch('threads.camera.Camera.run', new=DummyThread.run)
@patch('threads.notification.Notification.run', new=DummyThread.run)
def test_toggle_button_state(mock_factory):

    led_pin = mock_factory.pin(config.get('LED_GPIO_BCM'))
    button_pin = mock_factory.pin(config.get('BUTTON_GPIO_BCM'))

    button = Button()

    checkpoint = button.last_pressed
    button_pin.drive_low()  # button is pressed
    assert not led_pin.state
    assert checkpoint == button.last_pressed  # Do not ring. Pressed too fast
    time.sleep(0.1)
    button_pin.drive_high()  # button is released
    assert led_pin.state

    # Wait for threshold to expire
    time.sleep(int(config.get('BUTTON_PRESS_THRESHOLD', 1)))
    button_pin.drive_low()
    time.sleep(0.1)
    assert checkpoint != button.last_pressed
    button_pin.drive_high()


def test_ir_cut_off_toggle(mock_factory):

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
