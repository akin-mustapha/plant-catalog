import json
import logging
from service import NotificationDispatchService

logger = logging.getLogger()
logger.setLevel(logging.INFO)
    
def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    NotificationDispatchService().send_notifications()
    
    return {
        "statusCode": 200,
        "body": json.dumps(event)
    }
