# -*- code utf-8 -*-
print("buzzer")
from gpiozero import Buzzer
from time import sleep
print("Before")
bz = Buzzer(20)
#bz.beep(0.4, 0.4, 1)
bz.on()
sleep(0.4)
bz.off()
sleep(0.4)
bz.close()
print("Done!")
