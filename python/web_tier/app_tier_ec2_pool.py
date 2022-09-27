import boto3
from config_util import get_config_data
import datetime

config = get_config_data()


REGION_NAME= config['REGION_NAME']
REQUEST_QUEUE = config['REQUEST_QUEUE']
RESPONSE_QUEUE = config['RESPONSE_QUEUE']
INPUT_BUCKET = config['INPUT_BUCKET']
OUTPUT_BUCKET = config['OUTPUT_BUCKET']
IMAGES_DOWNLOAD_PATH = '/home/ubuntu/classifier/images'
CLASSIFICATION_MODEL_DIR = '/home/ubuntu/classifier'
TERMINATE_REQUEST_QUEUE = config['TERMINATE_REQUEST_QUEUE']
TERMINATE_CONFIRM_QUEUE=config['TERMINATE_CONFIRM_QUEUE']
CLASSIFIER_AMI = config['CLASSIFIER_AMI']
AWS_ACCESS_KEY_ID = config['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = config['AWS_SECRET_ACCESS_KEY']
KEY_NAME = config['KEY_NAME']

class AppTierEc2Pool:

    # Constructor call
    def __init__(self, maxInstances = 20, AMI=CLASSIFIER_AMI):
        self.maxInstances = maxInstances
        self.AMI = AMI
        self.shutdown_requests_count = 0
        self.instance_ids = [None] * (maxInstances + 1) #Stores in position 1 -> 20
        self.app_tier_available_ids = list(range(1, maxInstances + 1, 1)) # Pool of Available Ids for the instances

    # Get the SQS Resource in the the given region
    def get_SQS_Client(self):
        sqs_client = boto3.client(
            'sqs',
            region_name=REGION_NAME,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        return sqs_client

    # Get the S3 Resource in the the given region
    def get_EC2_Client(self):
        ec2_client = boto3.client(
            'ec2',
            region_name=REGION_NAME,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        return ec2_client

    # Creates a new instance of EC2 based on the parameters
    def create_ec2_instance(self):
        try:
            print(str(datetime.datetime.now()) + " Creating EC2 Instance")
            resource_ec2 = self.get_EC2_Client()

            app_tier_identifier = self.app_tier_available_ids.pop()
            
            # Startup script
            user_data = f"""#!/bin/bash
                cd /home/ubuntu/app_tier/
                pip3 install boto3;
                pip3 install pyyaml;
                su ubuntu -c "nohup python3 app_tier.py {app_tier_identifier}; exec sh"
                """

            response = resource_ec2.run_instances(
                ImageId= self.AMI,
                MinCount = 1,
                MaxCount = 1,
                InstanceType="t2.micro",
                KeyName=KEY_NAME,
                UserData = user_data,
                TagSpecifications=[{  # Give instance name based on App Tier ID
                    'ResourceType': 'instance',
                    'Tags': [{
                        'Key': 'Name',
                        'Value': f'app-instance{app_tier_identifier}'
                    }]
                }]
            )

            # Get the instance Id os the launched EC2
            ec2_instance_id = response['Instances'][0]['InstanceId']
            print(str(datetime.datetime.now()) + " Instance Id updated in the AppTierEc2Pool pool  ## Id : " + str(ec2_instance_id))
            self.instance_ids[app_tier_identifier] = ec2_instance_id

        except Exception as e:
            print(e)

    # Launch new EC2 instances based on the count provided
    def launch_instances(self, instanceCount):
        count = len(self.app_tier_available_ids)
        for _ in range(min(count, instanceCount)):
            self.create_ec2_instance()

    # Send messages to Terminate Request Queue based on the count provided
    def send_Request_to_Shutdown_Queue(self, requestCount):
        sqs_client = self.get_SQS_Client()

        for _ in range(requestCount):
            sqs_client.send_message(
                QueueUrl=TERMINATE_REQUEST_QUEUE,
                MessageBody='Terminate',
                DelaySeconds=0
            )
            self.shutdown_requests_count += 1

    # Cancel requests in the Queue based on the count provided. This is used to prevent shutdown of running instances
    #   when new requests have come
    def cancel_Request_In_Shutdown_Queue(self, cancelRequestCount):
        sqs_client = self.get_SQS_Client()
        loopSize = cancelRequestCount / 10
        
        while loopSize >= 0:
            response = sqs_client.receive_message(QueueUrl=TERMINATE_REQUEST_QUEUE, MaxNumberOfMessages=10)
            messages = response.get('Messages', [])
            loopSize = loopSize - 1
            
            for message in messages:
                msg_Identifier = message['ReceiptHandle']
                sqs_client.delete_message(QueueUrl=TERMINATE_REQUEST_QUEUE, ReceiptHandle=msg_Identifier)
                self.shutdown_requests_count -= 1
        return len(messages)

    # Inititate process to terminate the instance when the number of messages in Request Queue is less
    def terminate_EC2_Instances(self):
            sqs_client = self.get_SQS_Client()
            ec2_client = self.get_EC2_Client()
            response = sqs_client.receive_message(QueueUrl=TERMINATE_CONFIRM_QUEUE, MaxNumberOfMessages=10)
            messages = response.get('Messages', [])
            print(str(datetime.datetime.now()) + " Total instances to be terminated : " + str(len(messages)))
            
            for message in messages:
                msg_Identifier = message['ReceiptHandle']
                app_tier_identifier = int(message['Body'])
                if app_tier_identifier is not None:
                    ec2_client.terminate_instances(InstanceIds=[self.instance_ids[app_tier_identifier]])
                    self.instance_ids[app_tier_identifier] = None
                    # Push the app_tier Id back to the Instance Pool
                    self.app_tier_available_ids.append(app_tier_identifier)
                sqs_client.delete_message(QueueUrl=TERMINATE_CONFIRM_QUEUE, ReceiptHandle=msg_Identifier)
                self.shutdown_requests_count -= 1
