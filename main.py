import os
import sys
import time
import smbus
import math

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
g = 10

file.write("NewData "+str(now)+"\n")

while 1:
    imu.readSensor()
    for i in range(10):
        newTime = time.time()
        dt = newTime - currTime
        currTime = newTime

        sensorfusion.updateRollPitchYaw(imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2], imu.GyroVals[0], \
									imu.GyroVals[1], imu.GyroVals[2], imu.MagVals[0], imu.MagVals[1], imu.MagVals[2], dt)

    if print_count == 10:

        now = datetime.now()
        roll = sensorfusion.roll
        pitch = sensorfusion.pitch
        yaw = sensorfusion.yaw
        temp = imu.Temp

        file.write(str(now)+",")
        print("roll: " + str(roll))
        print("pitch: " + str(pitch))
        print("yaw: " + str(yaw))

        file.write(str(roll)+",")
        file.write(str(pitch)+",")
        file.write(str(yaw)+",")
        a = math.radians(roll - 90)
        b = math.radians(pitch + 90)
        c = math.radians(yaw+ 90)
       
        #delete

        ax = imu.AccelVals[0]
        ay = imu.AccelVals[1]
        az = imu.AccelVals[2]

        print("Ax " + str(ax))
        print("Ay " + str(ay))
        print("Az " + str(az))

        #delete

        if a < math.pi * -1:
            a = a + 2 * math.pi
        if b > math.pi:
            b = b - 2 * math.pi
        if c > math.pi:
            c = c - 2 * math.pi

        print("Grada: " + str(math.degrees(a)))
        print("Gradb: " + str(math.degrees(b)))
        print("Gradc: " + str(math.degrees(c)))

        if yaw*pitch < 0:
            ax = imu.AccelVals[0] - math.sqrt((g*math.tan(c)/math.sqrt((math.tan(c)** 2)/(math.cos(b) ** 2) +1)) ** 2)
        elif yaw*pitch > 0:
            ax = imu.AccelVals[0] + math.sqrt((g*math.tan(c)/math.sqrt((math.tan(c)** 2)/(math.cos(b) ** 2) +1)) ** 2)

        if yaw*roll < 0:
            ay = imu.AccelVals[1] - g/math.sqrt(math.tan(c) ** 2 + math.tan(a) ** 2 + 1 )
        elif yaw*roll > 0:
            ay = imu.AccelVals[1] + g/math.sqrt(math.tan(c) ** 2 + math.tan(a) ** 2 + 1 )
        
        if roll*pitch < 0:
            az = imu.AccelVals[2] - g/math.sqrt((1 / math.tan(a)) ** 2 + (1 / math.tan(b)) ** 2 + 1 )
        elif roll*pitch > 0:
            az = imu.AccelVals[2] + g/math.sqrt((1 / math.tan(a)) ** 2 + (1 / math.tan(b)) ** 2 + 1 )

        print("Ax " + str(ax))
        print("Ay " + str(ay))
        print("Az " + str(az))
        print("Temp: " + str(temp))

        file.write(str(temp))
        file.write("\n")

        print_count = 0

    print_count = print_count + 1
    time.sleep(0.01)
