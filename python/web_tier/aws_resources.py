from urllib import request
import boto3
import boto3.session
import uuid
import json
import datetime
from config_util import get_config_data

config = get_config_data()


REGION_NAME= config['REGION_NAME']
REQUEST_QUEUE = config['REQUEST_QUEUE']
RESPONSE_QUEUE = config['RESPONSE_QUEUE']
INPUT_BUCKET = config['INPUT_BUCKET']
OUTPUT_BUCKET = config['OUTPUT_BUCKET']
AWS_ACCESS_KEY_ID = config['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = config['AWS_SECRET_ACCESS_KEY']

my_session = boto3.session.Session()

# Get the S3 Resource in the the given region
def get_S3_Client():
    s3_client = my_session.client(
        's3',
        region_name=REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    return s3_client

# Get the SQS Resource in the the given region
def get_SQS_Client():
    sqs_client = my_session.client(
        'sqs',
        region_name=REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    return sqs_client

# Saves the image to the input bucket
def save_img_to_bucket(data, filename):
    s3_client = get_S3_Client()

    s3_client.upload_fileobj(
            data,
            INPUT_BUCKET,
            filename
    )

# Sends the image data to the Request SQS
def send_img_request_to_sqs(filename):
    request_id = str(uuid.uuid4())
    json_payload = {
        'filename': filename,
        'request_id': request_id
    }
    sqs = get_SQS_Client()

    sqs.send_message(
            QueueUrl=REQUEST_QUEUE,
            #MessageBody = filename,
            MessageBody=json.dumps(json_payload),
            DelaySeconds=0
    )
    return request_id

# def poll_response_queue(request_id):
#     sqs_client = get_SQS_Client()

    # messages = sqs_client.receive_message(QueueUrl=RESPONSE_QUEUE, MaxNumberOfMessages=10)
    # messages = messages.get('Messages', [])
    # for message in messages:
    #     msg_Identifier = message['ReceiptHandle']
    #     response = json.loads((message['Body']))
    #     if response['request_id'] == request_id:
    #         return response
    # return None

def poll_response_queue():
    sqs_client = get_SQS_Client()
    # total_messages_in_queue = get_Request_Queue_Size(RESPONSE_QUEUE)
    # print(str(datetime.datetime.now()) + f" Saving outputs of {total_messages_in_queue} messages from response queue")
    # while total_messages_in_queue>0:
    #     total_messages_in_queue = get_Request_Queue_Size(RESPONSE_QUEUE)
    messages = sqs_client.receive_message(QueueUrl=RESPONSE_QUEUE, MaxNumberOfMessages=1)
    messages = messages.get('Messages', [])
    if len(messages) > 0:
    # for message in messages:
        print(str(datetime.datetime.now()) + f" Retrieved a message from response queue")
        message = messages[0]
        msg_Identifier = message['ReceiptHandle']
        response = json.loads((message['Body']))
        # request_id = response['request_id']
        classifier_output = response['classifier_output']
        # f = open(f"output/{request_id}.txt", "a")
        # f.write(classifier_output)
        # f.close()
        sqs_client.delete_message(QueueUrl=RESPONSE_QUEUE, ReceiptHandle=msg_Identifier)
        return classifier_output
    else:
        return None
