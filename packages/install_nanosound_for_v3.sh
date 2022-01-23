#!/bin/bash

cd /home/volumio
rm -f nanosound_forv3.zip
rm -rf nanosound
wget https://github.com/nanomesher/Nanomesher_NanoSound/blob/master/packages/nanosound_forv3.zip
mkdir ./nanosound
miniunzip nanosound_forv3.zip -d ./nanosound
cd ./nanosound
volumio plugin install


echo "Cleaning up..."
cd /home/volumio
rm -f nanosound_forv3.zip
rm -rf nanosound