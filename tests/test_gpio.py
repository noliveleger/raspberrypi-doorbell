# -*- code utf-8 -*-
import time

from mock import patch

from helpers.config import config
from helpers.ircut import IRCutOff
from helpers.sundial import Sundial


class DummyThread:

    def run(self):
        return


@patch('helpers.bell.Bell.run', new=DummyThread.run)
@patch('helpers.camera.Camera.run', new=DummyThread.run)
@patch('helpers.telegram.Telegram.run', new=DummyThread.run)
def test_toggle_button_state(mock_factory):

    import daemon  # Has to be imported here, to mock led & button

    led_pin = mock_factory.pin(daemon.led.pin.number)
    button_pin = mock_factory.pin(daemon.button.pin.number)
    daemon.led.on()
    checkpoint = daemon.last_pressed
    daemon.button.when_pressed = daemon.button_pressed
    daemon.button.when_released = daemon.button_released

    button_pin.drive_low()  # button is pressed
    assert not led_pin.state
    assert checkpoint == daemon.last_pressed  # Do not ring. Pressed too fast
    time.sleep(0.1)
    button_pin.drive_high()  # button is released
    assert led_pin.state

    # Wait for threshold to expire
    time.sleep(int(config.get('BUTTON_PRESS_THRESHOLD', 1)))
    button_pin.drive_low()
    time.sleep(0.1)
    assert checkpoint != daemon.last_pressed
    button_pin.drive_high()

    daemon.led.close()
    daemon.button.close()


def test_ir_cut_off_day_mode(mock_factory):

    forward_pin = mock_factory.pin(config.get('IR_CUTOFF_FORWARD_PIN'))
    backward_pin = mock_factory.pin(config.get('IR_CUTOFF_BACKWARD_PIN'))
    enabler_pin = mock_factory.pin(config.get('IR_CUTOFF_ENABLER_PIN'))

    ir_cut_off = IRCutOff()
    ir_filter = ir_cut_off.toggle(Sundial.DAY)
    assert not forward_pin.state
    assert backward_pin.state
    assert enabler_pin.state
    time.sleep(0.1)
    ir_filter.stop()
    assert not forward_pin.state
    assert not backward_pin.state
    assert not enabler_pin.state
    time.sleep(0.1)
    ir_filter.close()


def test_ir_cut_off_night_mode(mock_factory):
    forward_pin = mock_factory.pin(config.get('IR_CUTOFF_FORWARD_PIN'))
    backward_pin = mock_factory.pin(config.get('IR_CUTOFF_BACKWARD_PIN'))
    enabler_pin = mock_factory.pin(config.get('IR_CUTOFF_ENABLER_PIN'))

    ir_cut_off = IRCutOff()
    ir_filter = ir_cut_off.toggle(Sundial.NIGHT)
    assert forward_pin.state
    assert not backward_pin.state
    assert enabler_pin.state
    time.sleep(0.1)
    ir_filter.stop()
    assert not forward_pin.state
    assert not backward_pin.state
    assert not enabler_pin.state
    time.sleep(0.1)
    ir_filter.close()
