import smbus
import time

import RPi.GPIO as gpio

PWR_M   = 0x6B
DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_EN   = 0x38
ACCEL_X = 0x3B
ACCEL_Y = 0x3D
ACCEL_Z = 0x3F
GYRO_X  = 0x43
GYRO_Y  = 0x45
GYRO_Z  = 0x47
TEMP = 0x41
bus = smbus.SMBus(1)

Device_Address = 0x68   # device address
AxCal=0
AyCal=0
AzCal=0
GxCal=0
GyCal=0
GzCal=0

def InitMPU():
     bus.write_byte_data(Device_Address, DIV, 7)
     bus.write_byte_data(Device_Address, PWR_M, 1)
     bus.write_byte_data(Device_Address, CONFIG, 0)
     bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
     bus.write_byte_data(Device_Address, INT_EN, 1)

def readMPU(addr):
     high = bus.read_byte_data(Device_Address, addr)
     low = bus.read_byte_data(Device_Address, addr+1)
     value = ((high << 8) | low)
     if(value > 32768):
           value = value - 65536
     return value

def accel():
     x = readMPU(ACCEL_X)
     y = readMPU(ACCEL_Y)
     z = readMPU(ACCEL_Z)
     Ax = (x/16384.0-AxCal)
     Ay = (y/16384.0-AyCal)
     Az = (z/16384.0-AzCal)
     print("X="+str(Ax))
     print("Y="+str(Ay))
     print("Z="+str(Az))

def gyro():
      global GxCal
      global GyCal
      global GzCal
      x = readMPU(GYRO_X)
      y = readMPU(GYRO_Y)
      z = readMPU(GYRO_Z)
      Gx = x/131.0 - GxCal
      Gy = y/131.0 - GyCal
      Gz = z/131.0 - GzCal
      print("gX="+str(Gx))
      print("gY="+str(Gy))
      print("gZ="+str(Gz))

def temp():
  tempRow=readMPU(TEMP)
  tempC=(tempRow / 340.0) + 36.53
  tempC="%.2f" %tempC
  print("Temp: ")
  print(str(tempC))

InitMPU()

while 1:
   temp()
   accel()
   gyro()
   time.sleep(.1)
