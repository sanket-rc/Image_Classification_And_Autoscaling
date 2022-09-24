from urllib import request
import boto3,time
from app_tier_ec2_pool import AppTierEc2Pool
import datetime
import json

from config_util import get_config_data

config = get_config_data()


REGION_NAME= config['REGION_NAME']
REQUEST_QUEUE = config['REQUEST_QUEUE']
RESPONSE_QUEUE = config['RESPONSE_QUEUE']
AWS_ACCESS_KEY_ID = config['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = config['AWS_SECRET_ACCESS_KEY']

# Get the SQS Resource in the the given region
def get_SQS_Client():
    sqs_client = boto3.client(
        'sqs',
        region_name=REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    return sqs_client

# Get the Request SQS Resource size
def get_Request_Queue_Size(queue_url):
    sqs_client = get_SQS_Client()

    response = sqs_client.get_queue_attributes(
        QueueUrl= queue_url,
        AttributeNames=['ApproximateNumberOfMessagesNotVisible', 'ApproximateNumberOfMessages']
    )

    # Messages which are consumed by a consumer
    undeleted_msg_count = int(response['Attributes']['ApproximateNumberOfMessagesNotVisible'])
    # Messages which are pending to be consumed
    visible_msg_count = int(response['Attributes']['ApproximateNumberOfMessages'])
    total_messages =  undeleted_msg_count + visible_msg_count
    return total_messages

def poll_response_queue():
    sqs_client = get_SQS_Client()
    total_messages_in_queue = get_Request_Queue_Size(RESPONSE_QUEUE)
    print(str(datetime.datetime.now()) + f" Saving outputs of {total_messages_in_queue} messages from response queue")
    while total_messages_in_queue>0:
        total_messages_in_queue = get_Request_Queue_Size(RESPONSE_QUEUE)
        messages = sqs_client.receive_message(QueueUrl=RESPONSE_QUEUE, MaxNumberOfMessages=10)
        messages = messages.get('Messages', [])
        for message in messages:
            msg_Identifier = message['ReceiptHandle']
            response = json.loads((message['Body']))
            request_id = response['request_id']
            classifier_output = response['classifier_output']
            f = open(f"output/{request_id}.txt", "a")
            f.write(classifier_output)
            f.close()
            sqs_client.delete_message(QueueUrl=RESPONSE_QUEUE, ReceiptHandle=msg_Identifier)

if __name__ == '__main__':
    ec2_pool = AppTierEc2Pool()

    while True:
        print(str(datetime.datetime.now()) + " Polling the Request queue for messages")
        total_messages_in_queue = get_Request_Queue_Size(REQUEST_QUEUE)
        total_active_instances = ec2_pool.maxInstances - ec2_pool.shutdown_requests_count - len(ec2_pool.app_tier_available_ids)

        total_required_instance = total_messages_in_queue - total_active_instances

        # Upscale when the required instance count is greater than 0
        if total_required_instance > 0:
            total_cancelled_requests = ec2_pool.cancel_Request_In_Shutdown_Queue(total_required_instance)
            print(str(datetime.datetime.now()) + " Cancelling {0} shutdown requests in Queue".format(total_cancelled_requests))
            required_instances = total_required_instance - total_cancelled_requests
            ec2_pool.launch_instances(required_instances)
        
        # Downscale when the required instance count is negative
        elif total_required_instance < 0 :
            delete_instance_count = abs(total_required_instance)
            print(str(datetime.datetime.now()) + " Deleting {0} instance of App Tier".format(delete_instance_count))
            ec2_pool.send_Request_to_Shutdown_Queue(delete_instance_count)
        
        ec2_pool.terminate_EC2_Instances()
        poll_response_queue()

        # Poll messages from the Request queue again after 10 seconds 
        time.sleep(10)
