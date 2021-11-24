import FaBo9Axis_MPU9250
import time
import sys
import math
from datetime import datetime

now = datetime.now()

file = open("./data/data.txt",'w') #change mode to 'a' whan merging, has to be 'a' when shipping

mpu9250 = FaBo9Axis_MPU9250.MPU9250()

calibrationfile = open("./config/mpuOffsets.txt")
ax_offs = calibrationfile.readline()
ay_offs = calibrationfile.readline()
az_offs = calibrationfile.readline()
gx_offs = calibrationfile.readline()
gy_offs = calibrationfile.readline()
gz_offs = calibrationfile.readline()
mx_offs = calibrationfile.readline()
my_offs = calibrationfile.readline()
mz_offs = calibrationfile.readline()
calibrationfile.close()

file.write("NewData "+str(now)+"\n")

while 1:
    now = datetime.now()
    accel = mpu9250.readAccel()
    gyro = mpu9250.readGyro()
    mag = mpu9250.readMagnet()
    temp = mpu9250.readTemperature()

    #Apply calibration values
    ax_cal = accel['x'] - float(ax_offs)
    ay_cal = accel['y'] - float(ay_offs)
    az_cal = accel['z'] - float(az_offs)

    gx_cal = gyro['x'] - float(gx_offs)
    gy_cal = gyro['y'] - float(gy_offs)
    gz_cal = gyro['z'] - float(gz_offs)

    mx_cal = mag['x'] - float(mx_offs)
    my_cal = mag['y'] - float(my_offs)
    mz_cal = mag['z'] - float(mz_offs)

    angx = math.atan2(mz_cal,my_cal)*180/math.pi
    if angx < 0:
        angx = 360 + angx

    angy = math.atan2(mz_cal,mx_cal)*180/math.pi
    if angy < 0:
        angy = 360 + angy

    angz = math.atan2(my_cal,mx_cal)*180/math.pi
    if angz < 0:
        angz = 360 + angz

    print(" ax = " , ax_cal)
    print(" ay = " , ay_cal)
    print(" az = " , az_cal)

    print(" gx = " , gx_cal)
    print(" gy = " , gy_cal)
    print(" gz = " , gz_cal)

    print(" mx = " , mx_cal)
    print(" my = " , my_cal)
    print(" mz = " , mz_cal)

    print(" Temp = " , temp)

    print("angx = " + str(angx))
    print("angy = " + str(angy))
    print("angz = " + str(angz))

    file.write(str(now)+"\n")
    time.sleep(0.2)
