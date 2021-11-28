# Run this script as root to get it working

import os
import time
import shutil

while 1:
    ismounted = os.path.ismount("/media/usb0")
    print("Device mounted: " + str(ismounted))
    if ismounted:
        shutil.copy("./data/data.txt","/media/usb0")
        print("copied!")
        while ismounted:
            ismounted = os.path.ismount("/media/usb0")
            print("remove drive!")
            time.sleep(1)
    time.sleep(1)
