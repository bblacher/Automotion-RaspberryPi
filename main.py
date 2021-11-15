import RPi.GPIO as GPIO
import time

sensor = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensor, GPIO.IN)

sample = 10
count = 0

start = 0
end = 0

def set_start():
    global start
    start = time.time()


def set_end():
    global end
    end = time.time()


def get_rpm(self):
    global count

    if not count:
            set_start()
            count = count + 1

    else:
            count = count + 1

            if count == sample:
                set_end()
                delta = end - start
                delta = delta / 60
                rpm = (sample / delta / 20)
                print(round(rpm,0))
                count = 0
                return 

GPIO.add_event_detect(sensor,GPIO.RISING, callback=get_rpm)

try:
        while True:
            time.sleep(0.1)
except KeyboardInterrupt:
            print ("   Quit")
            GPIO.cleanup()  
