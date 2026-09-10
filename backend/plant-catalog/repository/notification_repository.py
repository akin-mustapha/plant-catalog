import logging
from dataclasses import asdict

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from models import Notification

logger = logging.getLogger()


class NotificationRepository:
    def __init__(self):
        logger.info("Initialising DynamoDB resource")
        try:
            self.db = boto3.resource("dynamodb", region_name='eu-west-1')
        except ClientError as e:
            logger.error(e)

    def insert_notification(self, notification: Notification):
        logger.info(f"Inserting notification {notification.notification_id} into DB")
        try:
            table = self.db.Table("notification")
            table.put_item(Item=asdict(notification))
        except ClientError as e:
            logger.error(e)
            raise

    def select_by_plant_id(self, plant_id: str):
        logger.info(f"Selecting notification for plant id: {plant_id}")
        try:
            table = self.db.Table("notification")
            response = table.scan(
                FilterExpression=Attr("plant_id").eq(plant_id)
            )
            items = response["Items"]

            if not items:
                logger.info(f"No notification found for plant id: {plant_id}")
                return None

            item = items[0]
            logger.info(f"Selected notification {item.get('notification_id')}")

            return {k: (list(v) if isinstance(v, set) else v) for k, v in item.items()}
        except ClientError as e:
            logger.error(e)
            return None

    def select_by_id(self, notification_id: str):
        pass

    def update_notification_by_id(self, notification_id: str, notification):
        pass
