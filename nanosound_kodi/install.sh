#!/bin/bash

echo "Installing nanosound for kodi Dependencies"
sudo apt-get update

#sudo modprobe i2c_dev
# Install the required packages via apt-get

#sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 9165938D90FDDD2E

#START OF python devs
sudo apt-get -y install i2c-tools python-smbus python-pip python-dev python-imaging
sudo apt-get -y install python-setuptools
sudo apt-get -y install python-pip python-dev gcc
sudo pip install wheel
sudo pip install rpi.gpio
#sudo -H pip install --upgrade python-mpd2 socketIO-client


echo "Installing python services"

sudo chmod 777 ~/Nanomesher_NanoSound/nanosound_kodi/*.py

sudo cp ~/Nanomesher_NanoSound/nanosound_kodioled.service  /lib/systemd/system/
sudo cp ~/Nanomesher_NanoSound/nanomesher_piswitch.service  /lib/systemd/system/

sudo /bin/systemctl daemon-reload
sudo /bin/systemctl enable nanosound_kodioled.service
sudo /bin/systemctl start nanosound_kodioled.service
sudo /bin/systemctl enable nanomesher_piswitch.service
sudo /bin/systemctl start nanomesher_piswitch.service

echo "Nanosound for Kodi installed"