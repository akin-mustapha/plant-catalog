import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from .notification_repository import NotificationRepositoryFactory

    
notification_repo = NotificationRepositoryFactory.get("local")

notification_id = notification_repo.select_all()


print(f"Notification ID: {notification_id}")