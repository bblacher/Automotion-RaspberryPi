# RC-Car
DA Modellauto mit Sensorik

## Raspberry Pi Setup:

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
