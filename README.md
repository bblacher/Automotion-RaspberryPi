# RC-Car
DA Modellauto mit Sensorik

## Raspberry Pi Setup:
### Installing Raspberry Pi OS:
1. Download Raspberry Pi OS Lite from https://www.raspberrypi.com/software/operating-systems/
2. Use some imaging software to get the OS image onto the Raspberry Pi:
```sh
sudo fdisk -l
sudo cp ./image.img /dev/mmcblkX
```
3. Insert the micro SD card into the Raspberry Pi
4. Login using the default `pi` user with password `raspberry`
5. Get your system up-to-date:
```sh
sudo apt update
sudo apt upgrade
```
6. Use `sudo raspi-config`to enable SSH under "Interface Options"
7. Install python, pip, vim and ranger and uninsall nano
```sh
sudo apt install python pip vim ranger
sudo apt remove nano
```
### Automount USB thumb drive:
1. Install usbmount using apt:
```sh
sudo apt install usbmount
```
2. Change `PrivateMounts` to `no`:
```sh
sudo vim /lib/systemd/system/systemd-udevd.service
```
```sh
PrivateMounts=no
```
3. Edit `/etc/usbmount/usbmount.conf` to contain all needed file systems and mount with the right permissions:
```sh
sudo vim /etc/usbmount/usbmount.conf
```
Add `ntfs` to `FILESYSTEMS=""` and `-fstype=vfat,gid=users,dmask=0007,fmask=0117` to `FS_MOUNTOPTIONS=""`
