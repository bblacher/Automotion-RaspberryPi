import FaBo9Axis_MPU9250
import time
import sys
import math
from datetime import datetime

now = datetime.now()

#file = open("data.txt",'a')

#file.write("NewData "+str(now)+"\n")

mpu9250 = FaBo9Axis_MPU9250.MPU9250()

while 1:
    now = datetime.now()
    accel = mpu9250.readAccel()
    gyro = mpu9250.readGyro()
    mag = mpu9250.readMagnet()
    temp = mpu9250.readTemperature()


    #Apply calibration values

    ax_cal = accel['x'] - 0.008179822369812628
    ay_cal = accel['y'] - -0.0037405177991776117 
    az_cal = accel['z'] - 0.011897173006833461

    gx_cal = gyro['x'] - 1.5598297119140625
    gy_cal = gyro['y'] - 0.8936691284179688
    gz_cal = gyro['z'] - -0.0997161865234375

    mx_cal = mag['x'] - -6.73828125
    my_cal = mag['y'] - -45.99609375
    mz_cal = mag['z'] - -19.4091796875

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


    #file.write(str(now)+"\n")
    time.sleep(0.2)
