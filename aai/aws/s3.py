import boto3
import datetime
from io import BytesIO

# file_path = r'E:\KINO\Documents\GitHub\aai\aai\aws\sample\0-0-0-A_x80k-2.jpg'
# bucket_name = 'aai-test-company'
# object_name = 'sample/' + file_path.split('\\')[-1]
# file_path = ''
def upload_to_s3(file_path, bucket_name, object_name):
    """
    Upload file to S3 modified with rename upload file with the object_name
    :param file_path: Specify the file name, (the current setting is the file path).
    :param bucket_name: Specify the bucket name, eg. 'aai-test-company'
    :return: 3 different file locations for further access (s3_url,arn,object_url).
    """
    s3 = boto3.resource('s3')
    # with open(file_path, "rb") as f:
    # print(file_path)
        # s3.upload_fileobj(f.seek(0), bucket_name, object_name)
    print(object_name)
    s3.Bucket(bucket_name).put_object(Key=object_name, Body=file_path)
    s3_url = 's3://{}/{}'.format(bucket_name, object_name)
    arn = 'arn:aws:s3:::{}/{}'.format(bucket_name, object_name)
    object_url = 'https://{}.s3.amazonaws.com/{}'.format(bucket_name, object_name)
    return s3_url, arn, object_url

def download_from_s3_to_file(bucket_name, obj_from_s3, file_name):
    """
    Download file from S3 to disk location specified by file_name
    :param bucket_name: Specify the bucket name, eg. 'aai-test-company'
    :param obj_name: Specify the folder hierarhcy and object name
    :return: downloaded file object
    """
    s3 = boto3.client('s3')
    download_file = s3.download_file(bucket_name, obj_from_s3, file_name)
    return download_file


def download_from_s3_to_memory(bucket_name, obj_name):
    """
    Download file from S3 as BytesIO stream
    :param bucket_name: Specify the bucket name, eg. 'aai-test-company'
    :param obj_name: Specify the folder hierarhcy and object name
    :return: BytesIO stream
    """
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=obj_name)
    return BytesIO(response['Body'].read())