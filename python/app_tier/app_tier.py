from webbrowser import get
from flask import Flask , request
import boto3
#from botocore.config import Config
import traceback
import os
import json, sys, time,uuid

from config_util import get_config_data

config = get_config_data()


REGION_NAME= config['REGION_NAME']
REQUEST_QUEUE = config['REQUEST_QUEUE']
RESPONSE_QUEUE = config['RESPONSE_QUEUE']
INPUT_BUCKET = config['INPUT_BUCKET']
OUTPUT_BUCKET = config['OUTPUT_BUCKET']
IMAGES_DOWNLOAD_PATH = '/home/ubuntu/classifier'
CLASSIFICATION_MODEL_DIR = '/home/ubuntu/classifier'
TERMINATE_REQUEST_QUEUE = config['TERMINATE_REQUEST_QUEUE']
TERMINATE_CONFIRM_QUEUE=config['TERMINATE_CONFIRM_QUEUE']
# CLASSIFIER_AMI = config['CLASSIFIER_AMI']
AWS_ACCESS_KEY_ID = config['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = config['AWS_SECRET_ACCESS_KEY']

def get_S3_Client():
    s3_client = boto3.client(
        's3',
        region_name=REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    return s3_client

def get_SQS_Client():
    sqs_client = boto3.client(
        'sqs',
        region_name=REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    return sqs_client

def download_Image(image_path, image_name):
    s3_client = get_S3_Client()
    s3_client.download_file(INPUT_BUCKET, image_name, image_path)

def get_clasification_results(image_path):
    path = "cd {0}; python3 image_classification.py {1}".format(CLASSIFICATION_MODEL_DIR, image_path)
    result = os.popen(path).read()
    return result  #.strip()





while True:
    # Check for the Delay
    sqs_client = get_SQS_Client()
    s3_client = get_S3_Client()

    response = sqs_client.receive_message(QueueUrl = REQUEST_QUEUE) # Default no of messages polled  = 1
    print(response)

    sqs_request_messages = response.get('Messages', []) #----

    for sqs_message in sqs_request_messages:
        file_name = sqs_message['Body']
        identifier = sqs_message['ReceiptHandle']

        image_download_path = "{0}/{1}".format(IMAGES_DOWNLOAD_PATH, file_name)

        download_Image(image_download_path, file_name)

        classification_result = get_clasification_results(image_download_path)
        print("Classification Result : " + classification_result)

        #Send output data to SQS and S3 Bucket
        key = file_name.split('.')[0]
        body = "{0},{1}".format(key, classification_result)
        print("Key-value pair sent to response queue : " + body)

        s3_client.put_object(Key=key,Bucket= OUTPUT_BUCKET,Body=body)
        sqs_client.send_message(QueueUrl=RESPONSE_QUEUE, MessageBody=json.dumps({
            'id' : sys.argv[1],
            'classifier_output' : body
        })) # DelaySeconds ??

        # Delete the message from the Linux 
        os.remove(image_download_path)

        print('Deleting message...')
        sqs_client.delete_message(QueueUrl=REQUEST_QUEUE, ReceiptHandle = identifier)
        print('Message successfully deleted from Request Queue')
    
    response = sqs_client.receive_message(QueueUrl=TERMINATE_REQUEST_QUEUE) #, MaxNumberOfMessages=1)
    messages = response.get('Messages', [])
    
    if len(messages) > 0:
        msg_identifier = messages[0]['ReceiptHandle']
        print('In the process of Shutting down the instance')
        sqs_client.delete_message(QueueUrl=TERMINATE_REQUEST_QUEUE, ReceiptHandle = msg_identifier)
        
        # Send message to shutdown confirmed queue
        print('Sending message to Shutdown queue')
        sqs_client.send_message(QueueUrl=TERMINATE_CONFIRM_QUEUE,
               MessageBody=sys.argv[1],
               DelaySeconds=0,
            #    MessageDeduplicationId=str(uuid.uuid4()),
            #    MessageGroupId='2'
            )
        break  # Exit from loop

    ## Check with the professor
    time.sleep(4)





