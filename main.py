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
init_count = 0
g = 10

file.write("datetime,roll,pitch,yaw,ax,ay,az\n")

while init_count <= 150:
    imu.readSensor()
    for i in range(10):
        newTime = time.time()
        dt = newTime - currTime
        currTime = newTime
        sensorfusion.updateRollPitchYaw(imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2], imu.GyroVals[0], imu.GyroVals[1], imu.GyroVals[2], imu.MagVals[0], imu.MagVals[1], imu.MagVals[2], dt)
    init_count += 1
    time.sleep(0.01)

while 1:
    imu.readSensor()
    for i in range(10):
        newTime = time.time()
        dt = newTime - currTime
        currTime = newTime
        sensorfusion.updateRollPitchYaw(imu.AccelVals[0], imu.AccelVals[1], imu.AccelVals[2], imu.GyroVals[0], imu.GyroVals[1], imu.GyroVals[2], imu.MagVals[0], imu.MagVals[1], imu.MagVals[2], dt)

    if print_count == 10:

        now = datetime.now()
        roll = sensorfusion.roll
        pitch = sensorfusion.pitch
        yaw = sensorfusion.yaw
        temp = imu.Temp

        a = math.radians(roll - 90)
        b = math.radians(pitch + 90)
        c = math.radians(yaw)

        flipa = math.radians(roll - 180)
        flipb = math.radians(pitch)
       
        if a < math.pi * -1:
            a = a + 2 * math.pi

        if b > math.pi:
            b = b - 2 * math.pi

        if flipa < math.pi * -1:
            flipa = flipa + 2 * math.pi

        xoffs = math.sqrt(((g*math.tan(math.radians(90)))/math.sqrt((math.tan(math.radians(90))**2)/(math.cos(b)**2)+1))**2) 
        yoffs = g/math.sqrt((math.tan(0)**2)+(math.tan(a)**2)+1)
        zoffs = g/math.sqrt(((1/math.tan(a))**2)+((1/math.tan(b))**2)+1)

        if flipb < 0:
            ax = imu.AccelVals[0] - xoffs 
        elif flipb > 0:
            ax = imu.AccelVals[0] + xoffs

        if flipa < 0:
            ay = imu.AccelVals[1] - yoffs 
        elif flipa > 0:
            ay = imu.AccelVals[1] + yoffs
        
        if a*b < 0:
            az = imu.AccelVals[2] - zoffs
        elif a*b > 0:
            az = imu.AccelVals[2] + zoffs

        print("roll: " + str(roll))
        print("pitch: " + str(pitch))
        print("yaw: " + str(yaw))
        print("Ax " + str(ax))
        print("Ay " + str(ay))
        print("Az " + str(az))
        print("Temp: " + str(temp))

        file.write(str(now) + ",")
        file.write(str(roll)+ ",")
        file.write(str(pitch)+ ",")
        file.write(str(yaw)+ ",")
        file.write(str(ax)+ ",")
        file.write(str(ay)+ ",")
        file.write(str(az)+ ",")
        file.write(str(temp))
        file.write("\n")

        print_count = 0

    print_count = print_count + 1
    time.sleep(0.01)
