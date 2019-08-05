import RPi.GPIO as GPIO
import time

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def check():
    for i in range(10):
        input_state = GPIO.input(18)
        if input_state == False:
            return True
            time.sleep(0.01)
    return False
