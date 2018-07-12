import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
BUTTON_PIN = 21
LED_PIN = 17
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Button to GPIO23
GPIO.setup(LED_PIN, GPIO.OUT)  #LED to GPIO24

GPIO.output(LED_PIN, True)
try:
    while True:
         button_state = GPIO.input(BUTTON_PIN)
         if not button_state:
             GPIO.output(LED_PIN, False)
             print('Button Pressed...')
             time.sleep(0.2)
         else:
             GPIO.output(LED_PIN, True)
             pass
except Exception as e:
    print(str(e))

GPIO.cleanup()
