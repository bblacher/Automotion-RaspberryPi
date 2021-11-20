import RPi.GPIO as GPIO
import time

sensor = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

count = 0
slots = 20 

sample_time = 1

def count_rev(pin):
    global count
    count = count + 1

GPIO.add_event_detect(sensor, GPIO.RISING, callback=count_rev)

while True:
    time.sleep(sample_time)

    rpm = ((count / sample_time) * 60) / slots
    print(rpm)
    count = 0
