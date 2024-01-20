#!/bin/bash

echo "stap 1"
source venv/bin/activate
echo "stap 2"
/home/pi/git/openid-sn/python/venv/bin/python3 /home/pi/git/openid-sn/python/update_kampinfo.py >> /home/pi/git/openid-sn/python/output.log
echo "stap 3"
