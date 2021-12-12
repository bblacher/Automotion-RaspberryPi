import os
import sys
import time
import smbus
import math

from imusensor.MPU9250 import MPU9250
from imusensor.filters import madgwick
from datetime import datetime

g=10
roll = math.radians(-56.125) 
pitch = math.radians(0.000000000000000000001)
yaw = math.radians(-103)
print("roll: " + str(roll))
print("pitch: " + str(pitch))
print("yaw: " + str(yaw))

xoffs =math.sqrt(((g*math.tan(yaw))/math.sqrt((math.tan(yaw)**2)/(math.cos(pitch)**2)+1)) **2) 
yoffs =g/math.sqrt((math.tan(yaw)**2)+(math.tan(roll)**2)+1)
zoffs =g/math.sqrt(((1/math.tan(roll))**2)+((1/math.tan(pitch))**2)+1)

offsum = math.sqrt(xoffs ** 2 + yoffs ** 2 + zoffs ** 2)

print("Xoffs: " + str(xoffs))
print("Yoffs: " + str(yoffs))
print("Zoffs: " + str(zoffs))
print("Offsum: " + str(offsum))
