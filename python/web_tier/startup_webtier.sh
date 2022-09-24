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
python3 /home/ec2-user/web_tier/web_tier.py >> /home/ec2-user/web_tier/webtier_logs.txt &
python3 /home/ec2-user/web_tier/controller.py >> /home/ec2-user/web_tier/controller_logs.txt &
echo "Done" >> /home/ec2-user/startuplog.txt
