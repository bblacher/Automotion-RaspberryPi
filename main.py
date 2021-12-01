import os
import sys
import time
import smbus

from imusensor.MPU9250 import MPU9250
from imusensor.filters import madgwick
from datetime import datetime

if not os.path.exists('data'):
    os.makedirs('data')

now = datetime.now()

file = open("/home/pi/Diplomarbeit/RC-Car/data/data.txt",'w+') #change mode to 'a+' when merging, has to be 'a+' when shipping

sensorfusion = madgwick.Madgwick(0.5)

address = 0x68
bus = smbus.SMBus(1)
imu = MPU9250.MPU9250(bus, address)

imu.begin()

imu.loadCalibDataFromFile("/home/pi/Diplomarbeit/RC-Car/config/Calib.json")

currTime = time.time()

print_count = 0

while 1:
    imu.readSensor()
    for i in range(10):
        newTime = time.time()
        dt = newTime - currTime
        currTime = newTime

        sensorfusion.updateRollPitchYaw(imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2], imu.GyroVals[0], \
									imu.GyroVals[1], imu.GyroVals[2], imu.MagVals[0], imu.MagVals[1], imu.MagVals[2], dt)

    if print_count == 2:

        now = datetime.now()
        roll = sensorfusion.roll
        pitch = sensorfusion.pitch
        yaw = sensorfusion.yaw
        temp = imu.Temp

        if roll < 0:
            roll = 360 + roll

        if pitch < 0:
            pitch = 360 + pitch

        if yaw < 0:
            yaw = 360 + yaw

        print("roll: " + str(roll))
        print("pitch: " + str(pitch))
        print("yaw: " + str(yaw))
        print("Temp: " + str(temp))

        file.write(str(now)+",")
        file.write(str(roll)+",")
        file.write(str(pitch)+",")
        file.write(str(yaw)+",")
        file.write(str(temp)+",")
        file.write("\n")

        print_count = 0

    print_count = print_count + 1
    time.sleep(0.01)
