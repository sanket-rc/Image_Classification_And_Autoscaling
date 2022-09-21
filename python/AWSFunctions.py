import boto3
import os
from botocore.exceptions import ClientError


class AWSFunctions():
    def __init__(self, access_key, secret_key):
        self.secret_key = secret_key
        self.access_key = access_key

    def add_file_bucket(self, file_name, bucket, object_name):
        client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )
        if object_name is None:
            object_name = os.path.basename(file_name)

        s3_client = boto3.client('s3',
                                 aws_access_key_id=self.access_key,
                                 aws_secret_access_key=self.secret_key
                                 )
        try:
            response = s3_client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            print("error : " + e.response)
            return False
        return True


if __name__ == '__main__':
    ak = os.environ.get("AWS_ACCESS_KEY_ID")
    sk = os.environ.get("AWS_SECRET_ACCESS_KEY")
    obj = AWSFunctions(ak, sk)
    obj.add_file_bucket("aak.txt", "pro1input", "testfile")
