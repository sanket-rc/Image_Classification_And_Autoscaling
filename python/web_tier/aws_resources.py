from urllib import request
import boto3
import uuid
import json
from config_util import get_config_data

config = get_config_data()


REGION_NAME= config['REGION_NAME']
REQUEST_QUEUE = config['REQUEST_QUEUE']
RESPONSE_QUEUE = config['RESPONSE_QUEUE']
INPUT_BUCKET = config['INPUT_BUCKET']
OUTPUT_BUCKET = config['OUTPUT_BUCKET']
AWS_ACCESS_KEY_ID = config['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = config['AWS_SECRET_ACCESS_KEY']

# Get the S3 Resource in the the given region
def get_S3_Client():
    s3_client = boto3.client(
        's3',
        region_name=REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    return s3_client

# Get the SQS Resource in the the given region
def get_SQS_Client():
    sqs_client = boto3.client(
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
    # json_payload = {
    #     'filename': filename,
    #     'request_id': request_id
    # }
    sqs = get_SQS_Client()

    sqs.send_message(
            QueueUrl=REQUEST_QUEUE,
            MessageBody = filename,
            #MessageBody=json.dumps(json_payload),
            DelaySeconds=0
    )
    return request_id

# def poll_response_queue(request_id):
#     sqs_client = get_SQS_Client()

#     messages = sqs_client.receive_message(QueueUrl=RESPONSE_QUEUE, MaxNumberOfMessages=10)
#     messages = messages.get('Messages', [])
#     for message in messages:
#         msg_Identifier = message['ReceiptHandle']
#         response = json.loads((message['Body']))
#         if response['request_id'] == request_id:
#             return response
#     return None