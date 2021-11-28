# RC-Car
DA Modellauto mit Sensorik

Raspberry Pi Setup:

Automount USB thumb drive:

sudo apt install usbmount

sudo vim /lib/systemd/system/systemd-udevd.service
PrivateMounts=no

sudo vim /etc/usbmount/usbmount.conf
add ntfs to FILESYSTEMS="" and -fstype=vfat,gid=users,dmask=0007,fmask=0117 to FS_MOUNTOPTIONS=""
