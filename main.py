import serial       # Used for UART communication
import pynmea2      # Used for GPS Library
import os           # Used to check if a drive is mounted
import time         # Used for delays
import smbus        # Used for sensor access
import math         # Used for math operations
import shutil       # Used for file operations
import RPi.GPIO as GPIO  # Needed for GPIO actions (eg. Buttons)

from multiprocessing import Process, SimpleQueue  # Used for multiprocessing
from imusensor.MPU9250 import MPU9250   # Used for getting MPU9250 readings
from imusensor.filters import madgwick  # Used for the madgwick filter
from datetime import datetime           # Used for the madgwick filter timing


# Function definitions:
def empty_queue(queue):         # empty a given queue
    while not queue.empty():    # while it's not empty
        queue.get()             # get elements from it


def usb_automount():
    done = False    # init done as false
    global collecting_data
    while not done and not collecting_data:                     # only loop this while it's not done and not collecting data
        ismounted = os.path.ismount("/media/usb0")              # check if a drive is mounted
        print("Device mounted: " + str(ismounted))              # output drive mount status
        if ismounted:                                           # if a drive is mounted, copy the datafile to it
            try:                                                # try to copy the file
                for filename in os.listdir("./data/"):          # loop through all datafiles
                    shutil.copy("./data/"+filename, "/media/usb0")  # Copy the current file to the drive
                    print("copied!")                            # Confirmation that a file was copied successfully
            except:                                             # Error-Case: tell the user that the file wasn't copied
                print("copy error! (is there a datafile?)")     # Write the error
            while ismounted:                                    # while the device is mounted, tell the user to unplug it
                ismounted = os.path.ismount("/media/usb0")      # check the mount state of the drive
                print("remove drive!")                          # Tell the user to remove the drive
                done = True                                     # Break the automount loop
                time.sleep(1)                                   # 1-Second delay
        time.sleep(1)                                           # 1-Second delay


def sensor_fusion():
    currtime = time.time()      # get the current time for the first sensorfusion
    mpuerror = False            # init mpuerror as false
    calc_count = 0
    while not mpuerror:
        try:
            imu.readSensor()
            for fusionloop in range(10):  # get new sensor readings
                newtime = time.time()  # run the sensorfusion algorythm 10x faster than the sensor gets read
                dt = newtime - currtime  # get the new time
                currtime = newtime  # calculate the difference between the last and the new time
                sensorfusion.updateRollPitchYaw(imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2], imu.GyroVals[0],
                                                imu.GyroVals[1], imu.GyroVals[2], imu.MagVals[0], imu.MagVals[1],
                                                imu.MagVals[2], dt)  # call the sensorfusion algorithm
            if calc_count == 50:
                roll = sensorfusion.roll + 180  # get roll
                pitch = sensorfusion.pitch  # get pitch
                yaw = sensorfusion.yaw  # get yaw
                temp = imu.Temp  # get temp

                if roll > 180:  # if roll is now greater than 180
                    roll = roll - 360  # flip it by 360

                a = math.radians(roll - 90)  # flip the roll data by -90 degrees and save it into a
                b = math.radians(pitch + 90)  # flip the pitch data by 90 degrees and save it into a

                flipa = math.radians(roll - 180)  # flip the roll data by -180 degrees and save it into flipa

                if a < math.pi * -1:  # if a is now less than -pi
                    a = a + 2 * math.pi  # flip it by 2pi

                if b > math.pi:  # if a is now more than pi
                    b = b - 2 * math.pi  # flip it by -2pi

                if flipa < math.pi * -1:  # if flip a is now less than -pi
                    flipa = flipa + 2 * math.pi  # flip it by 2pi

                xoffs = math.sqrt(((g * math.tan(math.radians(90))) / math.sqrt(
                    (math.tan(math.radians(90)) ** 2) / (math.cos(b) ** 2) + 1)) ** 2)  # Offset in x
                yoffs = g / math.sqrt((math.tan(0) ** 2) + (math.tan(a) ** 2) + 1)  # Offset in y
                zoffs = g / math.sqrt(((1 / math.tan(a)) ** 2) + ((1 / math.tan(b)) ** 2) + 1)  # Offset in z

                if pitch < 0:  # check if x-Offset should be subtracted
                    ax = imu.AccelVals[0] - xoffs  # subtract x-Offset
                else:  # check if x-Offset should be added
                    ax = imu.AccelVals[0] + xoffs  # add x-Offset

                if flipa < 0:  # check if y-Offset should be subtracted
                    ay = imu.AccelVals[1] - yoffs  # subtract y-Offset
                else:  # check if y-Offset should be added
                    ay = imu.AccelVals[1] + yoffs  # add y-Offset

                if a * b < 0:  # check if z-Offset should be subtracted
                    az = imu.AccelVals[2] - zoffs  # subtract z-Offset
                else:  # check if z-Offset should be added
                    az = imu.AccelVals[2] + zoffs  # add z-Offset
                empty_queue(mpu_queue)  # empty the queue
                mpu_queue.put(str(roll)+","+str(pitch)+","+str(yaw)+","+str(ax)+","+str(ay)+","+str(az)+","+str(temp))
                calc_count = 0
            calc_count +=1
            time.sleep(0.01)

        except:
            empty_queue(mpu_queue)  # empty the queue
            mpu_queue.put("error,error,error,error,error,error,error")


def get_gps():
    gpserror = False        # set gpserror false
    while not gpserror:
        try:
            newdata = str(ser.readline())   # get new data
            newdata = newdata[2:-5]         # delete unwanted characters
            if newdata[0:6] == "$GPRMC":  # check if the right string is available
                newmsg = pynmea2.parse(newdata)  # parse new data
                lat = newmsg.latitude  # save latitude
                lng = newmsg.longitude  # save longitude
                empty_queue(gps_queue)  # empty the queue
                gps_queue.put(str(lat) + "," + str(lng))  # save gps data as string

        except:
            empty_queue(gps_queue)  # empty the queue
            gps_queue.put("error,error")    # set gps to error
            gpserror = True


def counter_rear_l(pin):                        # function for the rear left wheel count
    if not count_rear_L.empty():                # if the queue isn't empty, increase the count by 1
        tempvar = count_rear_L.get() + 1
        count_rear_L.put(tempvar)
    else:                                       # else, put 1 into the queue
        count_rear_L.put(1)


def counter_rear_r(pin):                        # function for the rear right wheel count
    if not count_rear_R.empty():                # if the queue isn't empty, increase the count by 1
        tempvar = count_rear_R.get() + 1
        count_rear_R.put(tempvar)
    else:                                       # else, put 1 into the queue
        count_rear_R.put(1)


def counter_front_l(pin):  # function for the front left wheel count
    if not count_front_L.empty():               # if the queue isn't empty, increase the count by 1
        tempvar = count_front_L.get() + 1
        count_front_L.put(tempvar)
    else:                                       # else, put 1 into the queue
        count_front_L.put(1)


def counter_front_r(pin):  # function for the front right wheel count
    if not count_front_R.empty():               # if the queue isn't empty, increase the count by 1
        tempvar = count_front_R.get() + 1
        count_front_R.put(tempvar)
    else:                                       # else, put 1 into the queue
        count_front_R.put(1)


def get_rpm(d_wheel, sample_time, slots_rear, slots_front):     # function for the rpm calculations
    while 1:
        time.sleep(sample_time)  # sleep for the sample time

        if not count_rear_L.empty():
            local_count_rear_l = count_rear_L.get()
        else:
            local_count_rear_l = 0

        if not count_rear_R.empty():
            local_count_rear_r = count_rear_R.get()
        else:
            local_count_rear_r = 0

        if not count_front_L.empty():
            local_count_front_l = count_front_L.get()
        else:
            local_count_front_l = 0

        if not count_front_R.empty():
            local_count_front_r = count_front_R.get()
        else:
            local_count_front_r = 0

        rpm_rear_l = ((float(local_count_rear_l) / slots_rear) / sample_time) * 60  # calculate the rpm
        rpm_rear_r = ((float(local_count_rear_r) / slots_rear) / sample_time) * 60  # calculate the rpm
        rpm_front_l = ((float(local_count_front_l) / slots_front) / sample_time) * 60   # calculate the rpm
        rpm_front_r = ((float(local_count_front_r) / slots_front) / sample_time) * 60   # calculate the rpm
        vel_ms = d_wheel * math.pi * (float((rpm_front_l + rpm_front_r) / 2) / 60)  # calculate the velocity as an average of the two front wheels
        empty_queue(count_rear_L)   # empty the queue
        empty_queue(count_rear_R)   # empty the queue
        empty_queue(count_front_L)  # empty the queue
        empty_queue(count_front_R)  # empty the queue
        rpm_queue.put(str(rpm_rear_l)+","+str(rpm_rear_r)+","+str(rpm_front_l)+","+str(rpm_front_r)+","+str(vel_ms))    # put the data into the queue


def print_data(u_mpu, u_rpm, u_gps):        # print the data (meant for debugging purposes)
    print("MPU: " + str(u_mpu))  # print roll
    print("RPM: " + str(u_rpm))  # print rpm
    print("GPS: " + str(u_gps))  # print gps


def write_data(u_now, u_mpu, u_rpm, u_gps):  # write the data to the internal sd card
    file.write(str(u_now) + ",")  # write Time
    file.write(str(u_mpu) + ",")  # write roll
    file.write(str(u_rpm) + ",")  # write rpm
    file.write(str(u_gps))  # write gps
    file.write("\n")  # write newline


def start_stop(pin):                            # function for switching modes
    global collecting_data
    collecting_data = not collecting_data       # invert collecting_data
    if not collecting_data:               # Also, close the file if data collection is stopped
        file.close()


if not os.path.exists('data'):  # If the data path doesn't exit, create it
    os.makedirs('data')

g = 10                                              # set g as 10
mpu_queue = SimpleQueue()                                  # init imuerror
try:                                                # Error handling for the IMU
    sensorfusion = madgwick.Madgwick(0.5)           # set Madgwick as the sensorfusion-algorythm
    address = 0x68                                  # MPU9250 I2C-Address
    bus = smbus.SMBus(1)                            # smbus for the imu
    imu = MPU9250.MPU9250(bus, address)             # set MPU9250 as the selected IMU
    imu.begin()                                     # begin IMU readings
    imu.loadCalibDataFromFile("./config/Calib.json")  # load calibration data
    process_sensorfusion = Process(target=sensor_fusion)  # create process for the sensorfusion
    process_sensorfusion.start()                    # start the process for the sensorfusion

except:                                             # Except-Statement for imuerror
    mpu_queue.put("error,error,error,error,error,error,error")
    print("MPU 9250: Error! (Not connected?)")      # Write error message


port = "/dev/ttyAMA0"                               # define UART device
ser = serial.Serial(port, baudrate=9600, timeout=0.5)  # set serial communication options
gps_queue = SimpleQueue()                           # create gps queue
gps_queue.put("error,error")                        # set gps to error,error (error code)
gps_process = Process(target=get_gps)               # create process for the gps module
gps_process.start()                                 # start the process for the gps module

collecting_data = False                             # init collecting_data
led = 37                                            # set the LED to PIN 37
modeswitch = 40                                     # set the modeswitch Button to PIN 40
GPIO.setmode(GPIO.BOARD)                            # Set GPIO to use Board pin layout
GPIO.setup(modeswitch, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # turn on pullup and set as input (modeswitch button)
GPIO.setup(led, GPIO.OUT)   # set as output (led)
GPIO.add_event_detect(modeswitch, GPIO.FALLING, callback=start_stop, bouncetime=1000)   # Attach interrupt to modeswitch

sensor_rear_L = 11      # set rear_L pin
sensor_rear_R = 12      # set rear_R pin
sensor_front_L = 13     # set front_L pin
sensor_front_R = 15     # set front_R pin
count_rear_L = SimpleQueue()         # create SimpleQueue
count_rear_R = SimpleQueue()         # create SimpleQueue
count_front_L = SimpleQueue()        # create SimpleQueue
count_front_R = SimpleQueue()        # create SimpleQueue
count_rear_L.put(0)                  # init as 0
count_rear_R.put(0)                  # init as 0
count_front_L.put(0)                 # init as 0
count_front_R.put(0)                 # init as 0
GPIO.setup(sensor_rear_L, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # turn on pulldown and set as input (rear_L)
GPIO.setup(sensor_rear_R, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # turn on pulldown and set as input (rear_R)
GPIO.setup(sensor_front_L, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # turn on pulldown and set as input (front_L)
GPIO.setup(sensor_front_R, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # turn on pulldown and set as input (front_R)
GPIO.add_event_detect(sensor_rear_L, GPIO.RISING, callback=counter_rear_l)  # Attach interrupt to rear_L
GPIO.add_event_detect(sensor_rear_R, GPIO.RISING, callback=counter_rear_r)  # Attach interrupt to rear_R
GPIO.add_event_detect(sensor_front_L, GPIO.RISING, callback=counter_front_l)    # Attach interrupt to front_L
GPIO.add_event_detect(sensor_front_R, GPIO.RISING, callback=counter_front_r)    # Attach interrupt to front_R
rpm_queue = SimpleQueue()                     # create queue for the rpm data
rpm_process = Process(target=get_rpm, args=(0.14, 1, 2, 2))   # create process for the gps module (args = d_wheel, sample_time, slots_rear, slots_front)
rpm_process.start()                     # start process for the gps module

while 1:                            # main loop
    if not collecting_data:   # if in usb-transfer mode
        usb_automount()             # call usb_automount
        GPIO.output(led, 0)  # turn LED off

    elif collecting_data:      # if in data collection mode
        GPIO.output(led, 1)  # turn LED on
        now = str(datetime.now())    # get datetime for the file name
        now = now.replace(' ', '_')  # replace blank space with underline for the file name
        now = now.replace(':', '_')  # replace colon with underline for the file name
        now = now.replace('.', '_')  # replace dot with underline for the file name
        file = open("./data/" + now + ".txt", 'w')  # create and open a new datafile
        file.write("datetime,roll,pitch,yaw,ax,ay,az,Temp,rpm_rear_l,rpm_rear_r,rpm_front_l,rpm_front_r,vel_ms,lat,lng\n")  # write the data legend into a new line
        while collecting_data:
            now = datetime.now()    # get datetime
            if not gps_queue.empty():
                gps = gps_queue.get()   # get gps data
            if not rpm_queue.empty():
                rpm = rpm_queue.get()   # get rpm data
            if not mpu_queue.empty():
                mpu = mpu_queue.get()   # get rpm data
            print_data(mpu, rpm, gps)         # print the data (meant for debugging purposes)
            write_data(now, mpu, rpm, gps)    # write the data to the internal sd card
            time.sleep(1)
