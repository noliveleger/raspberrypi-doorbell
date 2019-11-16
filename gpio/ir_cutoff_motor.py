# -*- code utf-8 -*-
from gpiozero import Motor


class IRCutOffMotor(Motor):

    def __init__(self, forward, backward, enable):
        super().__init__(forward=forward, backward=backward, enable=enable, pwm=False, pin_factory=None)

    def backward(self, speed=1):
        self.enable_device.on()
        super().backward(speed=speed)

    def forward(self, speed=1):
        self.enable_device.on()
        super().forward(speed=speed)

    def stop(self):
        super().stop()
        self.enable_device.off()
