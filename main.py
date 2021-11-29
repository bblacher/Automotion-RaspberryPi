# Run this script as root to get it working

import os   #Used to check if a drive is mounted
import time #Used for delays
import shutil   #Used for file operations

while 1:
    ismounted = os.path.ismount("/media/usb0")  #check if a drive is mounted
    print("Device mounted: " + str(ismounted))  #output drive mount status
    if ismounted:                               #if a drive is mounted, copy the datafile to it
        shutil.copy("./data/data.txt","/media/usb0")
        print("copied!")                        #Confirmation that the file was copied successfully
        while ismounted:                        #while the device is mounted, tell the user to unplug it
            ismounted = os.path.ismount("/media/usb0")
            print("remove drive!")      
            time.sleep(1)                       #1 Second delay
    time.sleep(1)                               #1 Second delay
