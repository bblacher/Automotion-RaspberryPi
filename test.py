import RPi.GPIO as GPIO
import time

sensor = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

count = 0
slots = 2
start = 0



def calculate(self):
    global count, start

    if not count:
        start = time.time()
        count = count + 1
    
    else:
        count = count + 1

        if time.time() - start <= 1:
            rpm = (count * 60 / slots)
            print(rpm)
            count = 0
            return

GPIO.add_event_detect(sensor,GPIO.RISING, callback=calculate)

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
        GPIO.cleanup()
