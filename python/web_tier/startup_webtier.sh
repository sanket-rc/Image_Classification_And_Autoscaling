#!/bin/bash
whoami >> /home/ec2-user/startuplog.txt
echo "Installation starting" >> /home/ec2-user/startuplog.txt
echo "Installing Flask" >> /home/ec2-user/startuplog.txt
pip3 install flask
echo "Installing pyyaml" >> /home/ec2-user/startuplog.txt
pip3 install pyyaml
echo "Installing boto3" >> /home/ec2-user/startuplog.txt
pip3 install boto3
echo "Installations Done" >> /home/ec2-user/startuplog.txt
chmod +x /home/ec2-user/web_tier
echo "xxxxxxxxxxxxxxxxxxxxxxxxxxx" >> /home/ec2-user/startuplog.txt
echo "running server" >> /home/ec2-user/startuplog.txt
cd /home/ec2-user/web_tier
echo "ran cd"
pwd
nohup python3 web_tier.py >> weblogs.txt &
sleep 50
echo "ran python web tier"
nohup python3 controller.py >> control_logs.txt &
sleep 50
echo "ran python controller"
echo "Done" >> /home/ec2-user/startuplog.txt
