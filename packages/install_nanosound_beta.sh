#!/bin/bash

cd /home/volumio
rm -f nanosound_beta.zip
rm -rf nanosound
wget https://github.com/nanomesher/Nanomesher_NanoSound/raw/master/packages/nanosound_beta.zip
mkdir ./nanosound
miniunzip nanosound_beta.zip -d ./nanosound
cd ./nanosound
volumio plugin install

echo "Cleaning up..."
cd /home/volumio
rm -f nanosound_beta.zip
rm -rf nanosound