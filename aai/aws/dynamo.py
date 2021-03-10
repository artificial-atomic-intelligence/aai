import boto3
import datetime

# file_path = r'E:\KINO\Documents\GitHub\aai\aai\aws\sample\0-0-0-A_x80k-2.jpg'
# bucket_name = 'aai-test-company'
# object_name = 'sample/' + file_path.split('\\')[-1]
# file_path = ''

# table_name = 'atomicai'
# key_schema = [{'AttributeName': 'user_name', 'KeyType': 'HASH'},
#               {'AttributeName': 'image_id', 'KeyType': 'RANGE'}]
# attribute_definitions = [{'AttributeName': 'user_name', 'AttributeType': 'S'},
#                          {'AttributeName': 'image_id', 'AttributeType': 'S'}]
def create_table(table_name, key_schema, attribute_definitions):
    """
    Create a new table in DynamoDB
    :param table_name:
    :param key_schema:
    :param attribute_definitions:
    :return:
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=key_schema,
        AttributeDefinitions=attribute_definitions,
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    return True


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
def create_single_item(table_name, item):
    """
    Upload a new item to DynamoDB table
    :param table_name:
    :param item:
    :return:
    """
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        table.put_item(Item=item)
        return True
    except Exception as e:
        return False



# table_name = 'atomicai'
# key = {'user_name': 'ethanli','image_id': 'img55665'}
def get_item(table_name, key):
    """
    Get a single item by referencing the user name and image id
    :param table_name:
    :param key:
    :return:
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    response = table.get_item(Key=key)
    item = response['Item']
    return item


# item = get_item(table_name, key)
# parameter_to_get = 'object_url'
def get_item_param(item, parameter_to_get):
    """
    Get a single parameter from the item
    :param item:
    :param parameter_to_get:
    :return:
    """
    return item[parameter_to_get]

