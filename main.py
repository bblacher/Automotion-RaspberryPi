import FaBo9Axis_MPU9250
import time
import sys
from datetime import datetime

now = datetime.now()

file = open("data.txt",'w')

file.write("NewData "+str(now)+"\n")

mpu9250 = FaBo9Axis_MPU9250.MPU9250()

while True:
    now = datetime.now()
    accel = mpu9250.readAccel()
    print(" ax = " , ( accel['x'] ))
    file.write(str(accel['x']*9.81)+",")
    print(" ay = " , ( accel['y'] ))
    file.write(str(accel['y']*9.81)+",")
    print(" az = " , ( accel['z'] ))
    file.write(str(accel['z']*9.81)+",")

    #gyro = mpu9250.readGyro()
    #print(" gx = " , ( gyro['x'] ))
    #print(" gy = " , ( gyro['y'] ))
    #print(" gz = " , ( gyro['z'] ))

    #mag = mpu9250.readMagnet()
    #print(" mx = " , ( mag['x'] ))
    #print(" my = " , ( mag['y'] ))
    #print(" mz = " , ( mag['z'] ))

    #temp = mpu9250.readTemperature()
    #print(" Temp = " , temp)

    file.write(str(now)+"\n")
    time.sleep(0.2)
