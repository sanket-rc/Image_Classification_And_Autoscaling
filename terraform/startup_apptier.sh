#!/bin/bash
echo "Installation starting" >> /home/ubuntu/startuplog.txt
echo "Installing Flask" >> /home/ubuntu/startuplog.txt
pip3 install flask
echo "Installing pyyaml" >> /home/ubuntu/startuplog.txt
pip3 install pyyaml
echo "Installing boto3" >> /home/ubuntu/startuplog.txt
pip3 install boto3
echo "Installations Done" >> /home/ubuntu/startuplog.txt
chmod +x /home/ubuntu/app_tier
cho "Done" >> /home/ubuntu/startuplog.txt