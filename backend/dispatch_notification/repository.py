import logging
from dataclasses import asdict

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from models import NotificationLog, Notification

logger = logging.getLogger()


class NotificationRepository:
    def __init__(self):
        logger.info("Initialising DynamoDB resource")
        try:
            self.db = boto3.resource("dynamodb", region_name='eu-west-1')
        except ClientError as e:
            logger.error(e)

    def insert_notification_log(self, notification_log: NotificationLog):
        logger.info(f"Inserting notification log {notification_log.notification_id} into DB")
        try:
            table = self.db.Table("notification_log")
            table.put_item(Item=asdict(notification_log))
        except ClientError as e:
            logger.error(e)
            raise

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


class NotificationRepositoryLocal:
    def __init__(self):
        logger.info("Initialising Local Repository")
        self.db = None

    def select_all(self):
        logger.info("Selecting all notifications from local repository")
        
        return [{'user_id': None, 'interval': None, 'schedule': '0 9 * * 1', 'next_run_date': '2026-09-10T15:23:57.348260+00:00', 'contacts': ['you@emp.com'], 'type_id': 'watering-reminder', 'status': 'ACTIVE', 'topic_arn': None, 'notification_id': 'd383c57c-fa07-4d96-b990-6f0b159572d1', 'description': '', 'name': 'Test'}, {'user_id': None, 'interval': None, 'plant_id': '34f46ab0-e99d-4adc-a0ff-a4953359e98e', 'schedule': '0 9 * * 1', 'next_run_date': '2026-09-10T15:38:07.679668+00:00', 'contacts': [{'email': 'test@eosne.com', 'status': 'pending'}], 'type_id': 'watering-reminder', 'status': 'ACTIVE', 'topic_arn': None, 'notification_id': '76292aab-6cee-4c71-a381-de74b0e9ed8f', 'description': '', 'name': 'test'}]


class NotificationRepositoryFactory:
    @staticmethod
    def get(env: str = "local"):
        if env == "local":
            return NotificationRepositoryLocal()
        else:
            return NotificationRepository()
        