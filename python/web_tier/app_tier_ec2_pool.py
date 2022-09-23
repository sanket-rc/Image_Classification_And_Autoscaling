import boto3
import uuid
from config_util import get_config_data

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

    def __init__(self, maxInstances = 20, AMI=CLASSIFIER_AMI):
        self.maxInstances = maxInstances
        self.AMI = AMI
        self.shutdown_requests_count = 0
        #self.app_tier_ids = [None] * (maxInstances + 1) #Ignore the Index 0 position -> 21 size
        self.instance_ids = [None] * (maxInstances + 1) #Ignore the Index 0 position -> 21 size
        self.app_tier_available_ids = list(range(1, maxInstances + 1, 1)) # 1 to 20

    def get_SQS_Client(self):
        sqs_client = boto3.client(
            'sqs',
            region_name=REGION_NAME,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        return sqs_client

    def get_EC2_Client(self):
        ec2_client = boto3.client(
            'ec2',
            region_name=REGION_NAME,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        return ec2_client

    def create_ec2_instance(self): # Incompletee +++++++++++++++++++++++++++++
        try:
            print("Creating EC2 Instance")
            resource_ec2 = self.get_EC2_Client()

            app_tier_identifier = self.app_tier_available_ids.pop()
            # Startup script
            user_data = f"""#!/bin/bash
                pip3 install flask;
                pip3 install boto3;
                pip3 install pyyaml;
                su ubuntu -c "python3 /home/ubuntu/app_tier/app_tier.py {app_tier_identifier}; exec sh"
                """
            # runuser -l ubuntu -c 'screen -dm bash -c "python3 /home/ubuntu/app_tier/app_tier.py {app_tier_identifier}; exec sh"'
            # su ec2-user -c 'do whatever you want; ./run.sh &'
            response = resource_ec2.run_instances(
                ImageId= self.AMI,
                MinCount = 1,
                MaxCount = 1,
                InstanceType="t2.micro",
                KeyName=KEY_NAME,
                UserData = user_data

            )
            ec2_instance_id = response['Instances'][0]['InstanceId']
            #instance = AppTierInstance(instance_id=instance_id, app_tier_id=app_tier_id)
            #self.app_tier_ids[app_tier_identifier] = app_tier_identifier
            print("Instance Id updated in the AppTierEc2Pool pool")
            self.instance_ids[app_tier_identifier] = ec2_instance_id
            #return instance

        except Exception as e:
            print(e)

    def launch_instances(self, instanceCount):
        count = len(self.app_tier_available_ids)
        for _ in range(min(count, instanceCount)):
            self.create_ec2_instance()

    def send_Request_to_Shutdown_Queue(self, requestCount):
        sqs_client = self.get_SQS_Client()

        for _ in range(requestCount):
            sqs_client.send_message(
                QueueUrl=TERMINATE_REQUEST_QUEUE,
                MessageBody='Terminate',
                DelaySeconds=0,
                # MessageDeduplicationId=str(uuid.uuid4()),
                # MessageGroupId='1'
            )
            self.shutdown_requests_count += 1

    def cancel_Request_In_Shutdown_Queue(self, cancelRequestCount):
        sqs_client = self.get_SQS_Client()

        response = sqs_client.receive_message(QueueUrl=TERMINATE_REQUEST_QUEUE, MaxNumberOfMessages=min(cancelRequestCount, 10)) #?????????
        messages = response.get('Messages', [])
        #print('Cancelling', len(messages), 'shutdown requests.')
        for message in messages:
            msg_Identifier = message['ReceiptHandle']
            sqs_client.delete_message(QueueUrl=TERMINATE_REQUEST_QUEUE, ReceiptHandle=msg_Identifier)
            self.shutdown_requests_count -= 1
        return len(messages)

    def terminate_EC2_Instances(self):
            sqs_client = self.get_SQS_Client()
            ec2_client = self.get_EC2_Client()
            response = sqs_client.receive_message(QueueUrl=TERMINATE_CONFIRM_QUEUE, MaxNumberOfMessages=10)
            messages = response.get('Messages', [])
            print('Found', len(messages), 'shutdown confirmed messages.') # Change this comment
            # Respond to each shutdown confirmed message
            for message in messages:
                msg_Identifier = message['ReceiptHandle']
                app_tier_identifier = int(message['Body'])
                if app_tier_identifier is not None:
                    ec2_client.terminate_instances(InstanceIds=[self.instance_ids[app_tier_identifier]])
                    self.instance_ids[app_tier_identifier] = None
                    self.app_tier_available_ids.append(app_tier_identifier)
                sqs_client.delete_message(QueueUrl=TERMINATE_CONFIRM_QUEUE, ReceiptHandle=msg_Identifier)
                self.shutdown_requests_count -= 1
