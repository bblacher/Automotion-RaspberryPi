import serial       # Used for UART communication
import pynmea2      # Used for GPS Library
import os           # Used to check if a drive is mounted
import time         # Used for delays
import smbus        # Used for sensor access
import math         # Used for math operations
import shutil       # Used for file operations
import RPi.GPIO as GPIO  # Needed for GPIO actions (eg. Buttons)

from multiprocessing import Process, Queue     # Used for multiprocessing
from imusensor.MPU9250 import MPU9250   # Used for getting MPU9250 readings
from imusensor.filters import madgwick  # Used for the madgwick filter
from datetime import datetime           # Used for the madgwick filter timing


# Function definitions:
def usb_automount():
    done = False    # init done as false
    while not done and not collecting_data:                     # only loop this while it's not done and in usb transfer mode
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
    global imuerror
    currtime = time.time()
    while not imuerror:
        try:
            imu.readSensor()
            for fusionloop in range(10):  # get new sensor readings
                newtime = time.time()  # run the sensorfusion algorythm 10x faster than the sensor gets read
                dt = newtime - currtime  # get the new time
                currtime = newtime  # calculate the difference between the last and the new time
                sensorfusion.updateRollPitchYaw(imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2], imu.GyroVals[0],
                                                imu.GyroVals[1], imu.GyroVals[2], imu.MagVals[0], imu.MagVals[1],
                                                imu.MagVals[2], dt)  # call the sensorfusion algorithm
            time.sleep(0.01)
        except:
            imuerror = True


def get_gps():
    gpserror = False
    while not gpserror:
        try:
            ser = serial.Serial(port, baudrate=9600, timeout=0.5)  # set serial communication options
            newdata = str(ser.readline())                                   # get new data
            newdata = newdata[2:-5]                                         # delete unwanted characters
            if newdata[0:6] == "$GPRMC":                                    # check if the right string is available
                newmsg = pynmea2.parse(newdata)                             # parse new data
                lat = newmsg.latitude                                       # save latitude
                lng = newmsg.longitude                                      # save longitude
                gps_queue.put(str(lat) + "," + str(lng))                    # save gps data as string
        except:
            gps_queue.put("error,error")                                          # set gps to -1,-1 (error code)
            gpserror = True
    

def print_data(u_roll, u_pitch, u_yaw, u_ax, u_ay, u_az, u_temp, u_gps):        # print the data (meant for debugging purposes)
    print("roll: " + str(u_roll))  # print roll
    print("pitch: " + str(u_pitch))  # print pitch
    print("yaw: " + str(u_yaw))  # print yaw
    print("Ax " + str(u_ax))  # print ax
    print("Ay " + str(u_ay))  # print ay
    print("Az " + str(u_az))  # print az
    print("Temp: " + str(u_temp))  # print temp
    print("GPS: " + str(u_gps))  # print gps


def write_data(u_now, u_roll, u_pitch, u_yaw, u_ax, u_ay, u_az, u_temp, u_gps):  # write the data to the internal sd card
    file.write(str(u_now) + ",")  # write Time
    file.write(str(u_roll) + ",")  # write roll
    file.write(str(u_pitch) + ",")  # write pitch
    file.write(str(u_yaw) + ",")  # write yaw
    file.write(str(u_ax) + ",")  # write ax
    file.write(str(u_ay) + ",")  # write ay
    file.write(str(u_az) + ",")  # write az
    file.write(str(u_temp) + ",")  # write temp
    file.write(str(u_gps))  # write gps
    file.write("\n")  # write newline


def start_stop(pin):                        # function for switching modes
    global collecting_data                  # use global collecting_data
    collecting_data = not collecting_data   # invert collecting_data
    if not collecting_data:                 # Also, close the file if data collection is stopped
        file.close()


if not os.path.exists('data'):  # If the data path doesn't exit, create it
    os.makedirs('data')


try:                                                # Error handling for the IMU
    sensorfusion = madgwick.Madgwick(0.5)           # set Madgwick as the sensorfusion-algorythm
    address = 0x68                                  # MPU9250 I2C-Address
    bus = smbus.SMBus(1)                            # smbus for the imu
    imu = MPU9250.MPU9250(bus, address)             # set MPU9250 as the selected IMU
    imu.begin()                                     # begin IMU readings
    imu.loadCalibDataFromFile("./config/Calib.json")  # load calibration data
    imuerror = False                                # Set imuerror false for later use
    process_sensorfusion = Process(target=sensor_fusion)  # create thread for the sensorfusion
    process_sensorfusion.start()                    # start the thread for the sensorfusion
except:                                             # Except-Statement for imuerror
    print("MPU 9250: Error! (Not connected?)")      # Write error message
    imuerror = True                                 # Set imuerror true for later use

g = 10                                              # set g as 10
port = "/dev/ttyAMA0"                               # define UART device
gps = "error,error"                                 # set gps to -1,-1 (error code)
gps_queue = Queue()
process_gps = Process(target=get_gps)               # create thread for the sensorfusion
process_gps.start()                                 # start the thread for the sensorfusion

collecting_data = False                             # init collecting_data
modeswitch = 40                                     # set the modeswitch Button to PIN 40
GPIO.setmode(GPIO.BOARD)                            # Set GPIO to use Board pin layout
GPIO.setup(modeswitch, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # turn on pullup and set as input modeswitch button)
GPIO.add_event_detect(modeswitch, GPIO.FALLING, callback=start_stop, bouncetime=1000)   # Attach interrupt to modeswitch

while 1:                            # main loop
    if not collecting_data:         # if in usb-transfer mode
        usb_automount()             # call usb_automount

    elif collecting_data:            # if in data collection mode
        now = str(datetime.now())    # get datetime for the file name
        now = now.replace(' ', '_')  # replace blank space with underline for the file name
        now = now.replace(':', '_')  # replace colon with underline for the file name
        now = now.replace('.', '_')  # replace dot with underline for the file name
        file = open("./data/" + now + ".txt", 'w')  # create and open a new datafile
        file.write("datetime,roll,pitch,yaw,ax,ay,az,Temp,lat,lng\n")  # write the data legend into a new line
        while collecting_data:
            now = datetime.now()                    # get datetime
            if not imuerror:
                roll = sensorfusion.roll                # get roll
                pitch = sensorfusion.pitch              # get pitch
                yaw = sensorfusion.yaw                  # get yaw
                temp = imu.Temp                         # get temp

                a = math.radians(roll - 90)             # flip the roll data by -90 degrees and save it into a
                b = math.radians(pitch + 90)            # flip the pitch data by 90 degrees and save it into a

                flipa = math.radians(roll - 180)        # flip the roll data by -180 degrees and save it into flipa

                if a < math.pi * -1:                    # if a is now less than -pi
                    a = a + 2 * math.pi                 # flip it by 2pi

                if b > math.pi:                         # if a is now more than pi
                    b = b - 2 * math.pi                 # flip it by -2pi

                if flipa < math.pi * -1:                # if flip a is now less than -pi
                    flipa = flipa + 2 * math.pi         # flip it by 2pi

                xoffs = math.sqrt(((g * math.tan(math.radians(90))) / math.sqrt((math.tan(math.radians(90)) ** 2) / (math.cos(b) ** 2) + 1)) ** 2)  # Offset in x
                yoffs = g / math.sqrt((math.tan(0) ** 2) + (math.tan(a) ** 2) + 1)              # Offset in y
                zoffs = g / math.sqrt(((1 / math.tan(a)) ** 2) + ((1 / math.tan(b)) ** 2) + 1)  # Offset in z

                if pitch < 0:                       # check if x-Offset should be subtracted
                    ax = imu.AccelVals[0] - xoffs   # subtract x-Offset
                elif pitch > 0:                     # check if x-Offset should be added
                    ax = imu.AccelVals[0] + xoffs   # add x-Offset

                if flipa < 0:                       # check if y-Offset should be subtracted
                    ay = imu.AccelVals[1] - yoffs   # subtract y-Offset
                elif flipa > 0:                     # check if y-Offset should be added
                    ay = imu.AccelVals[1] + yoffs   # add y-Offset

                if a * b < 0:                       # check if z-Offset should be subtracted
                    az = imu.AccelVals[2] - zoffs   # subtract z-Offset
                elif a * b > 0:                     # check if z-Offset should be added
                    az = imu.AccelVals[2] + zoffs   # add z-Offset

            elif imuerror:
                roll = "error"  # write error into imusensor values
                pitch = "error"  # write error into imusensor values
                yaw = "error"  # write error into imusensor values
                ax = "error"  # write error into imusensor values
                ay = "error"  # write error into imusensor values
                az = "error"  # write error into imusensor values
                temp = "error"  # write error into imusensor values

            gps = gps_queue.get()
            print_data(roll, pitch, yaw, ax, ay, az, temp, gps)         # print the data (meant for debugging purposes)
            write_data(now, roll, pitch, yaw, ax, ay, az, temp, gps)    # write the data to the internal sd card
            time.sleep(1)
