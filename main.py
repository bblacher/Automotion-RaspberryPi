# Run this script as root to get it working

import os  # Used to check if a drive is mounted
import time  # Used for delays
import smbus  # Used for sensor access
import math  # Used for math operations
import shutil  # Used for file operations

from imusensor.MPU9250 import MPU9250  # Used for getting MPU9250 readings
from imusensor.filters import madgwick  # Used for the madgwick filter
from datetime import datetime  # Used for the madgwick filter timing

if not os.path.exists('data'):  # If the data path doesn't exit, create it
    os.makedirs('data')

file = open("/home/pi/Diplomarbeit/RC-Car/data/data.txt", 'a+')  # Open the datafile in append-mode if it exists, create it if it doesn't exist

sensorfusion = madgwick.Madgwick(0.5)           # set Madgwick as the sensorfusion-algorythm
address = 0x68                                  # MPU9250 I2C-Address
bus = smbus.SMBus(1)                            # smbus for the imu
imu = MPU9250.MPU9250(bus, address)             # set MPU9250 as the selected IMU
try:                                            # Error handling for the IMU
    imu.begin()                                 # begin IMU readings
except:                                         # Except-Statement for imuerror
    print("MPU 9250: Error! (Not connected?)")  # Write error message
    imuerror = True                             # Set imuerror true for later use
imu.loadCalibDataFromFile("/home/pi/Diplomarbeit/RC-Car/config/Calib.json")  # load calibration data
currTime = time.time()  # save the current time for the sensorfusion
print_count = 0  # init print_count
g = 10  # set g as 10

file.write("datetime,roll,pitch,yaw,ax,ay,az\n")  # write the data legend into a new line
if not imuerror:
    for i in range(150):  # do the sensorfusion 150 times to get the initial wrong data out of the way
        imu.readSensor()
        for i in range(10):
            newTime = time.time()
            dt = newTime - currTime
            currTime = newTime
            sensorfusion.updateRollPitchYaw(imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2], imu.GyroVals[0],
                                            imu.GyroVals[1], imu.GyroVals[2], imu.MagVals[0], imu.MagVals[1],
                                            imu.MagVals[2], dt)
        time.sleep(0.01)

    while 1:  # main loop if the imu has no error
        imu.readSensor()  # get new sensor readings
        for i in range(10):  # run the sensorfusion algorythm 10x faster than the sensor gets read
            newTime = time.time()  # get the new time
            dt = newTime - currTime  # calculate the difference between the last and the new time
            currTime = newTime  # write the new time into currTime for the next cycle
            sensorfusion.updateRollPitchYaw(imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2], imu.GyroVals[0],
                                            imu.GyroVals[1], imu.GyroVals[2], imu.MagVals[0], imu.MagVals[1],
                                            imu.MagVals[2], dt)  # call the sensorfusion algorithm

        if print_count == 10:  # every 10 cycles write the data to the SD Card

            now = datetime.now()  # get datetime
            roll = sensorfusion.roll  # get roll
            pitch = sensorfusion.pitch  # get pitch
            yaw = sensorfusion.yaw  # get yaw
            temp = imu.Temp  # get temp

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
            elif pitch > 0:  # check if x-Offset should be added
                ax = imu.AccelVals[0] + xoffs  # add x-Offset

            if flipa < 0:  # check if y-Offset should be subtracted
                ay = imu.AccelVals[1] - yoffs  # subtract y-Offset
            elif flipa > 0:  # check if y-Offset should be added
                ay = imu.AccelVals[1] + yoffs  # add y-Offset

            if a * b < 0:  # check if z-Offset should be subtracted
                az = imu.AccelVals[2] - zoffs  # subtract z-Offset
            elif a * b > 0:  # check if z-Offset should be added
                az = imu.AccelVals[2] + zoffs  # add z-Offset

            print("roll: " + str(roll))  # print roll
            print("pitch: " + str(pitch))  # print pitch
            print("yaw: " + str(yaw))  # print yaw
            print("Ax " + str(ax))  # print ax
            print("Ay " + str(ay))  # print ay
            print("Az " + str(az))  # print az
            print("Temp: " + str(temp))  # print temp

            file.write(str(now) + ",")  # write Time
            file.write(str(roll) + ",")  # write roll
            file.write(str(pitch) + ",")  # write pitch
            file.write(str(yaw) + ",")  # write yaw
            file.write(str(ax) + ",")  # write ax
            file.write(str(ay) + ",")  # write ay
            file.write(str(az) + ",")  # write az
            file.write(str(temp))  # write temp
            file.write("\n")  # write newline

            print_count = 0  # reset print count

        print_count += 1  # up print count by 1
        time.sleep(0.01)  # wait for 10 milliseconds

elif imuerror:
    print(imuerror)


# Keeping usb-automount deactivated till button activation is implemented
# while 1:
#    ismounted = os.path.ismount("/media/usb0")  #check if a drive is mounted
#    print("Device mounted: " + str(ismounted))  #output drive mount status
#    if ismounted:                               #if a drive is mounted, copy the datafile to it
#        shutil.copy("./data/data.txt","/media/usb0")
#        print("copied!")                        #Confirmation that the file was copied successfully
#        while ismounted:                        #while the device is mounted, tell the user to unplug it
#            ismounted = os.path.ismount("/media/usb0")
#            print("remove drive!")      
#            time.sleep(1)                       #1-Second delay
#    time.sleep(1)                               #1-Second delay
