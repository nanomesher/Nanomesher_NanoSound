#!/bin/bash

cd /home/volumio
rm -f nanosound.zip
rm -rf nanosound
wget https://github.com/nanomesher/Nanomesher_NanoSound/raw/master/packages/nanosound.zip
mkdir ./nanosound
miniunzip nanosound.zip -d ./nanosound
cd ./nanosound
volumio plugin install

echo "Cleaning up..."
cd /home/volumio
rm -f nanosound.zip
rm -rf nanosound