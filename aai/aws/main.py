import boto3
from dynamo import *

# upload given file to S3
# file_path = r'E:\KINO\Documents\GitHub\aai\aai\aws\sample\0-0-0-A_x80k-2.jpg'
# bucket_name = 'aai-test-company'
# object_name = 'sample/' + file_path.split('\\')[-1]
# s3_url, arn, object_url = upload_to_s3(file_path, bucket_name, object_name)

# create a new table on DynamoDB
table_name = 'users'
key_schema = [{'AttributeName': 'user_name', 'KeyType': 'HASH'},
              {'AttributeName': 'passwd', 'KeyType': 'RANGE'}]
attribute_definitions = [{'AttributeName': 'user_name', 'AttributeType': 'S'},
                         {'AttributeName': 'passwd', 'AttributeType': 'S'}]
# res = create_table(table_name, key_schema, attribute_definitions)
# print(res)

# Upload the metadata of the uploaded file to DynamoDB
# table_name = 'atomicai'
# item = {'user_name': 'ethanli',
#         'company_name': 'atomicai',
#         'first_name': 'ethan',
#         'last_name': 'li',
#         'project_name': 'database test',
#         'sample_id': '152x3x0',
#         'image_id': 'img8686',
#         's3_url': s3_url,
#         'arn': arn,
#         'object_url': object_url,
#         'file_name': object_name,
#         }
# create_single_item(table_name, item)

# table_name = 'atomicai'
# key = {'user_name': 'ethanli','image_id': 'img55665'}
# response = get_item(table_name, key)


# parameter_to_get = 'object_url'
# object_url = get_item_param(item, parameter_to_get)
# print(object_url)

