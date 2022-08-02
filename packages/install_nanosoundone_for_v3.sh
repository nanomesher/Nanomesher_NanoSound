#!/bin/bash

cd /home/volumio
rm -f nanosoundone_forv3.zip
rm -rf nanosoundone
wget https://github.com/nanomesher/Nanomesher_NanoSound/raw/master/packages/nanosoundone_forv3.zip
mkdir ./nanosoundone
miniunzip nanosoundone_forv3.zip -d ./nanosoundone
cd ./nanosoundone
volumio plugin install


echo "Cleaning up..."
cd /home/volumio
rm -f nanosoundone_forv3.zip
rm -rf nanosoundone