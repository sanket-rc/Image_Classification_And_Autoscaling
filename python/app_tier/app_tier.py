from webbrowser import get
from flask import Flask , request
import boto3
import os
import json, sys, time,uuid
import datetime


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
AWS_ACCESS_KEY_ID = config['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = config['AWS_SECRET_ACCESS_KEY']

#
# Get the S3 Resource in the the given region
#
def get_S3_Client():
    s3_client = boto3.client(
        's3',
        region_name=REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    return s3_client

#
# Get the SQS Resource in the the given region
#
def get_SQS_Client():
    sqs_client = boto3.client(
        'sqs',
        region_name=REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    return sqs_client

#
# Download the Image from the Input Bucket in given location as parameter
#
def download_Image(image_path, image_name):
    s3_client = get_S3_Client()
    s3_client.download_file(INPUT_BUCKET, image_name, image_path)

#
# Does image recognition using the directory of the input image
#
def get_clasification_results(image_path):
    path = "cd {0}; python3 image_classification.py {1}".format(CLASSIFICATION_MODEL_DIR, image_path)
    result = os.popen(path).read()
    return result


while True:
    # Gets the S3 and SQS resources
    sqs_client = get_SQS_Client()
    s3_client = get_S3_Client()

    response = sqs_client.receive_message(QueueUrl = REQUEST_QUEUE) # Default number of messages polled  = 1
    print(response)

    sqs_request_messages = response.get('Messages', [])

    if len(sqs_request_messages) > 0:
        sqs_message = sqs_request_messages[0]
        file_name = sqs_message['Body']
        identifier = sqs_message['ReceiptHandle']

        # Get the image download path
        image_download_path = "{0}/{1}".format(IMAGES_DOWNLOAD_PATH, file_name)

        download_Image(image_download_path, file_name)

        classification_result = get_clasification_results(image_download_path)
        print("Classification Result : " + classification_result)

        #Send output data to SQS and S3 Bucket
        key = file_name.split('.')[0]
        body = "{0},{1}".format(key, classification_result)
        print(str(datetime.datetime.now()) + " Key-value pair sent to response queue : " + body)

        s3_client.put_object(Key=key,Bucket= OUTPUT_BUCKET,Body=body)
        sqs_client.send_message(QueueUrl=RESPONSE_QUEUE, MessageBody=json.dumps({
            'request_id' : sys.argv[1],
            'classifier_output' : body
        }))

        print(str(datetime.datetime.now()) + '########## Deleting message from the Request Queue ##########')
        sqs_client.delete_message(QueueUrl=REQUEST_QUEUE, ReceiptHandle = identifier)
        print(str(datetime.datetime.now()) + ' Message successfully deleted from Request Queue')
    
    # Checks the Terminate Request Queue after each request meaages is procesed
    response = sqs_client.receive_message(QueueUrl=TERMINATE_REQUEST_QUEUE)
    messages = response.get('Messages', [])

    # Starts process to terminate the instance
    if len(messages) > 0:
        msg_identifier = messages[0]['ReceiptHandle']
        print(str(datetime.datetime.now()) + ' In the process of termnating the instance')
        sqs_client.delete_message(QueueUrl=TERMINATE_REQUEST_QUEUE, ReceiptHandle = msg_identifier)
        
        # Send message to shutdown confirmed queue
        print(str(datetime.datetime.now()) + ' Sending message to Terminate Confirm Queue')
        sqs_client.send_message(QueueUrl=TERMINATE_CONFIRM_QUEUE,
               MessageBody=sys.argv[1],
               DelaySeconds=0
            )
        break  # Exit from loop

    # Poll messages from the Request queue again after 5 seconds 
    time.sleep(5)





