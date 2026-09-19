import json
import logging

import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from notification_repository import NotificationRepository


logger = logging.getLogger()
logger.setLevel(logging.INFO)


## Connect to DynamoDB
# try:
#     db_client = boto3.resource("dynamodb", region_name='eu-west-1')
#     table = db_client.Table("notification")
# except ClientError as e:
#     logger.error(e)
    
    
def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    notification_repo = NotificationRepository()
    
    notification_id = notification_repo.select_all()

    return {
        "statusCode": 200,
        "body": json.dumps(notification_id)
    }
