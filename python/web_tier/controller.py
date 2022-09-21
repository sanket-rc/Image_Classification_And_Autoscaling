import boto3,time
from app_tier_ec2_pool import AppTierEc2Pool

from config_util import get_config_data

config = get_config_data()


REGION_NAME= config['REGION_NAME']
REQUEST_QUEUE = config['REQUEST_QUEUE']
AWS_ACCESS_KEY_ID = config['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = config['AWS_SECRET_ACCESS_KEY']


def get_SQS_Client():
    sqs_client = boto3.client(
        'sqs',
        region_name=REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    return sqs_client

def get_Request_Queue_Size():
    sqs_client = get_SQS_Client()

    response = sqs_client.get_queue_attributes(
        QueueUrl= REQUEST_QUEUE,
        AttributeNames=['ApproximateNumberOfMessagesNotVisible', 'ApproximateNumberOfMessages']
    )

    undeleted_msg_count = int(response['Attributes']['ApproximateNumberOfMessagesNotVisible'])
    visible_msg_count = int(response['Attributes']['ApproximateNumberOfMessages'])
    # print('Undeleted Message Count in Request Queue : ' + str(undeleted_msg_count))
    # print('Visible Message Count in Request Queue : ' + str(visible_msg_count))
    total_messages =  undeleted_msg_count + visible_msg_count

    return total_messages

if __name__ == '__main__':
    ec2_pool = AppTierEc2Pool()

    while True:
        total_messages_in_queue = get_Request_Queue_Size()
        total_projected_instances = ec2_pool.maxInstances - ec2_pool.shutdown_requests_count - len(ec2_pool.app_tier_available_ids)

        total_required_instance = total_messages_in_queue - total_projected_instances

        # print("Project instance count : {0} & Required Instance count : {1}".format(total_projected_instances, total_required_instance))

        if total_required_instance > 0:
            total_cancelled_requests = ec2_pool.cancel_Request_In_Shutdown_Queue(total_required_instance)
            print("Cancelling {0} shutdown requests in Queue".format(total_cancelled_requests))
            required_instances = total_required_instance - total_cancelled_requests
            ec2_pool.launch_instances(required_instances)
        
        else:
            delete_instance_count = abs(total_required_instance)
            # print("Deleting {0} instance of App Tier".format(delete_instance_count))
            ec2_pool.send_Request_to_Shutdown_Queue(delete_instance_count)
        
        ec2_pool.terminate_EC2_Instances()

        #time.sleep(7)
