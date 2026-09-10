import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()


class NotificationRepository:
    def __init__(self):
        logger.info("Initialising DynamoDB resource")
        try:
            self.db = boto3.resource("dynamodb", region_name='eu-west-1')
        except ClientError as e:
            logger.error(e)

    def insert_notification(self, notification):
        pass

    def select_by_user_id(self, user_id: str):
        pass

    def select_by_id(self, notification_id: str):
        pass

    def update_notification_by_id(self, notification_id: str, notification):
        pass
