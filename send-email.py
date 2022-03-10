import boto3
import time

ses_client = boto3.client('ses')
db_resource = boto3.resource('dynamodb')
table = db_resource.Table('token_table')


def NotifyUser(event, context):
    args = event["Records"][0]['Sns']['Message'].split()
    recipient = args[0]
    domain = args[1]
    token = args[2]

    status = get_record(token)
    if not status:
        ses_client.send_email(
            Source='csye6225@' + domain,
            Destination={
                'ToAddresses': [
                    recipient
                ]
            },
            Message={
                'Subject': {
                    'Data': 'Register Verification'
                },
                'Body': {
                    'Text': {
                        'Data': 'Please click https://' + domain + '/v1/user/verify/' + token + ' to verify yourself.'
                    }
                }
            }
        )
        insert_record(token)
        return "notify the user successfully"
    else:
        return "duplicate message"


def insert_record(record):
    response = table.put_item(
        Item={
            "token": record,
            "ttl": int(time.time()) + 120
        }
    )
    return response["ResponseMetadata"]["HTTPStatusCode"]


def get_record(record):
    response = table.get_item(
        Key={
            "token": record
        }
    )
    if 'Item' in response:
        return True
    else:
        return False
