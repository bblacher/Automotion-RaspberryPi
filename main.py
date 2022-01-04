import RPi.GPIO as GPIO
import time
import math
from multiprocessing import Process, Queue     # Used for multiprocessing

def counter_rear_l(pin):
    global count_rear_l
    count_rear_l = count_rear_l + 1


def counter_rear_r(pin):
    global count_rear_r
    count_rear_r = count_rear_r + 1


def counter_front_l(pin):
    global count_front_l
    count_front_l = count_front_l + 1


def counter_front_r(pin):
    global count_front_r
    count_front_r = count_front_r + 1

def get_rpm():
    d_wheel = 0.14
    sample_time = 1
    slots_rear = 20
    slots_front = 20
    while 1:
        time.sleep(sample_time)
        rpm_rear_l = ((float(count_rear_l) / slots_rear) / sample_time) * 60
        rpm_rear_r = ((float(count_rear_r) / slots_rear) / sample_time) * 60
        rpm_front_l = ((float(count_front_l) / slots_front) / sample_time) * 60
        rpm_front_r = ((float(count_front_r) / slots_front) / sample_time) * 60
        vel_ms = d_wheel * math.pi * (float((rpm_front_l + rpm_front_r) / 2) / 60)
        count_rear_l = 0
        count_rear_r = 0
        count_front_l = 0
        count_front_r = 0
        rpm_queue.put(str(rpm_rear_l)+","+str(rpm_rear_r)+","+str(rpm_front_l)+","+str(rpm_front_r)+","+str(vel_ms))


sensor_rear_L = 11
sensor_rear_R = 12
sensor_front_L = 13
sensor_front_R = 15

GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensor_rear_L, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sensor_rear_R, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sensor_front_L, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sensor_front_R, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(sensor_rear_L, GPIO.RISING, callback=counter_rear_l)
GPIO.add_event_detect(sensor_rear_R, GPIO.RISING, callback=counter_rear_r)
GPIO.add_event_detect(sensor_front_L, GPIO.RISING, callback=counter_front_l)
GPIO.add_event_detect(sensor_front_R, GPIO.RISING, callback=counter_front_r)

rpm_queue = Queue()
rpm_process = Process(target=get_rpm)
rpm_process.start()




