# coding: utf-8
import time

from mock import patch
from gpiozero.pins.mock import PinState

from app.config import config
from app.devices.button import Button
from app.helpers import Singleton
from app.helpers.sundial import Sundial
from app.devices.ir_cut_off import IRCutOff
from app.threads.chime import Chime
from . import (
    MockSocket,
    MockThread,
)


@patch('socket.socket', new=MockSocket)
@patch('app.threads.camera.Camera.run', new=MockThread.run)
@patch('app.threads.notification.Notification.run', new=MockThread.run)
def test_press_button_too_fast(mock_factory):

    led_pin = mock_factory.pin(config.get('LED_GPIO_BCM'))
    button_pin = mock_factory.pin(config.get('BUTTON_GPIO_BCM'))
    chime_pin = mock_factory.pin(config.get('CHIME_GPIO_BCM'))

    button = Button()
    checkpoint = button.last_pressed
    button_pin.drive_low()  # button is pressed
    assert checkpoint == button.last_pressed  # Do not ring. Pressed too fast

    expected_states = [PinState(timestamp=0.0, state=False)]
    chime_pin.assert_states_and_times(expected_states)

    Singleton.destroy(Button)


@patch('socket.socket', new=MockSocket)
@patch('app.threads.camera.Camera.run', new=MockThread.run)
@patch('app.threads.notification.Notification.run', new=MockThread.run)
def test_press_button_normally(mock_factory):
    led_pin = mock_factory.pin(config.get('LED_GPIO_BCM'))
    button_pin = mock_factory.pin(config.get('BUTTON_GPIO_BCM'))
    chime_pin = mock_factory.pin(config.get('CHIME_GPIO_BCM'))

    button = Button()
    checkpoint = button.last_pressed
    # Wait for threshold to expire before pressing the button
    time.sleep(int(config.get('BUTTON_PRESS_THRESHOLD', 1)))
    chime_start = chime_pin._last_change
    button_pin.drive_low()  # button is pressed
    assert checkpoint != button.last_pressed

    # Verify Chime state changes
    now = time.time()
    # Have to wait that the thread has completed
    time.sleep(Chime.PAUSE_BETWEEN_STATES * 2)
    warm_up_offset = 0.10
    expected_states = [
        PinState(timestamp=0.0, state=False),
        PinState(timestamp=now - (chime_start + warm_up_offset), state=True),
        PinState(timestamp=Chime.PAUSE_BETWEEN_STATES, state=False),
    ]

    chime_pin.assert_states_and_times(expected_states)
    Singleton.destroy(Button)


@patch('socket.socket', new=MockSocket)
@patch('app.threads.camera.Camera.run', new=MockThread.run)
@patch('app.threads.notification.Notification.run', new=MockThread.run)
def test_led(mock_factory):
    led_pin = mock_factory.pin(config.get('LED_GPIO_BCM'))
    button_pin = mock_factory.pin(config.get('BUTTON_GPIO_BCM'))
    chime_pin = mock_factory.pin(config.get('CHIME_GPIO_BCM'))

    button = Button()
    button.activate_led()

    # Force LED to be always on
    button._led_always_on = True
    button_pin.drive_low()  # button is pressed
    assert not led_pin.state
    assert led_pin.state == button.led.is_lit
    time.sleep(0.1)
    button_pin.drive_high()  # button is released
    assert led_pin.state
    assert led_pin.state == button.led.is_lit

    # Force LED to be on during the day
    button._led_always_on = False
    button_pin.drive_low()  # button is pressed
    should_be_lit = not Sundial().is_day()
    assert led_pin.state is not should_be_lit
    time.sleep(0.1)
    button_pin.drive_high()  # button is released
    assert led_pin.state is should_be_lit

    Singleton.destroy(Button)


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

    Singleton.destroy(IRCutOff)
