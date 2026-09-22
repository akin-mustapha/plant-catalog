import logging
from dataclasses import asdict

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from models import Notification, Contact, NotificationContact

logger = logging.getLogger()


class NotificationRepository:
    def __init__(self):
        logger.info("Initialising DynamoDB resource")
        try:
            self.db = boto3.resource("dynamodb", region_name='eu-west-1')
        except ClientError as e:
            logger.error(e)

    def insert_to_table(self, table_name: str, item: dict):
        logger.info(f"Inserting item into {table_name} table")
        try:
            table = self.db.Table(table_name)
            table.put_item(Item=item)
        except ClientError as e:
            logger.error(e)
            raise
    def insert_notification(self, notification: Notification):
        logger.info(f"Inserting notification {notification.notification_id} into DB")
        self.insert_to_table("notification", asdict(notification))
        
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

    def select_all(self):
        logger.info("Selecting all notifications")
        try:
            table = self.db.Table("notification")
            response = table.scan()
            items = response["Items"]
            logger.info(f"Selected {len(items)}")

            return [
                {k: (list(v) if isinstance(v, set) else v) for k, v in item.items()}
                for item in items
            ]
        except ClientError as e:
            logger.error(e)

    def select_by_id(self, notification_id: str):
        logger.info(f"Selecting notification by id: {notification_id}")
        try:
            table = self.db.Table("notification")
            response = table.get_item(Key={"notification_id": notification_id})

            item = response.get("Item")
            if item is None:
                logger.info(f"No notification found for id: {notification_id}")
                return None

            logger.info(f"Selected {len(item)}")

            return {k: (list(v) if isinstance(v, set) else v) for k, v in item.items()}
        except ClientError as e:
            logger.error(e)
            return None

    def update_notification_by_id(self, notification_id: str, notification: Notification):
        logger.info(f"Updating notification by id: {notification_id}")
        try:
            table = self.db.Table("notification")
            table.update_item(
                Key={
                    "notification_id": notification_id
                },
                UpdateExpression="""
                    set #ty=:ty,
                    #n=:n,
                    #d=:d,
                    #st=:st,
                    #c=:c,
                    #u=:u,
                    #sc=:sc,
                    #i=:i,
                    #nr=:nr,
                    #ta=:ta
                """,
                ExpressionAttributeNames={
                    "#ty": "type_id",
                    "#n": "name",
                    "#d": "description",
                    "#st": "status",
                    "#c": "contacts",
                    "#u": "user_id",
                    "#sc": "schedule",
                    "#i": "interval",
                    "#nr": "next_run_date",
                    "#ta": "topic_arn"
                },
                ExpressionAttributeValues={
                    ":ty": notification.type_id,
                    ":n": notification.name,
                    ":d": notification.description,
                    ":st": notification.status,
                    ":c": notification.contacts,
                    ":u": notification.user_id,
                    ":sc": notification.schedule,
                    ":i": notification.interval,
                    ":nr": notification.next_run_date,
                    ":ta": notification.topic_arn
                },
                ConditionExpression=Attr("notification_id").exists()
            )
        except ClientError as e:
            logger.error(e)
            return {"message": "Notification update failed"}

        logger.info(f"Updated {notification_id}")

        return {"message": "Notification updated successfully"}

    def delete_by_id(self, notification_id: str):
        logger.info(f"Deleting notification by id: {notification_id}")
        try:
            table = self.db.Table("notification")
            table.delete_item(Key={"notification_id": notification_id})
        except ClientError as e:
            logger.error(e)
            return {"message": "Notification delete failed"}

        logger.info(f"Deleted {notification_id}")

        return {"message": "Notification deleted successfully"}
