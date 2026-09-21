import json
import logging

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
    return {
        "statusCode": 200,
        "body": json.dumps(event)
    }
