#!/bin/bash

cd /home/volumio
rm -f nanosoundone.zip
rm -rf nanosoundone
wget https://github.com/nanomesher/Nanomesher_NanoSound/raw/master/packages/nanosoundone.zip
mkdir ./nanosoundone
miniunzip nanosoundone.zip -d ./nanosoundone
cd ./nanosoundone
volumio plugin install

echo "Cleaning up..."
cd /home/volumio
rm -f nanosoundone.zip
rm -rf nanosoundone
