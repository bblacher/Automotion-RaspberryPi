import RPi.GPIO as GPIO
import time
import math

sensor_rear_L = 11
sensor_rear_R = 12
sensor_front_L = 13
sensor_front_R = 15

GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensor_rear_L, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sensor_rear_R, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sensor_front_L, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sensor_front_R, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

count_rear_L = 0
count_rear_R = 0
count_front_L = 0
count_front_R = 0

slots_rear = 20 
slots_front = 20
d_wheel = 0.14
sample_time = 1

def counter_rear_L(pin):
    global count_rear_L
    count_rear_L = count_rear_L + 1

def counter_rear_R(pin):
    global count_rear_R
    count_rear_R = count_rear_R + 1

def counter_front_L(pin):
    global count_front_L
    count_front_L = count_front_L + 1

def counter_front_R(pin):
    global count_front_R
    count_front_R = count_front_R + 1

GPIO.add_event_detect(sensor_rear_L, GPIO.RISING, callback=counter_rear_L) 
GPIO.add_event_detect(sensor_rear_R, GPIO.RISING, callback=counter_rear_R)  
GPIO.add_event_detect(sensor_front_L, GPIO.RISING, callback=counter_front_L)
GPIO.add_event_detect(sensor_front_R, GPIO.RISING, callback=counter_front_R)

while True:
    time.sleep(sample_time)

    rpm_rear_L = ((float(count_rear_L) / slots_rear) / sample_time) * 60
    rpm_rear_R = ((float(count_rear_R) / slots_rear) / sample_time) * 60
    rpm_front_L = ((float(count_front_L) / slots_front) / sample_time) * 60
    rpm_front_R = ((float(count_front_R) / slots_front) / sample_time) * 60
   # vel_ms = d_wheel * math.pi * (float(rpm) / 60)
    print(rpm_rear_L)
    print(rpm_rear_R)
    print(rpm_front_L)
    print(rpm_front_R)
  #  print(vel_ms)
  #  print(vel_ms * 3.6)
    count_rear_L = 0
    count_rear_R = 0
    count_front_L = 0
    count_front_R = 0
