import logging
from dataclasses import asdict

import boto3
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

from models import Activity

logger = logging.getLogger()


class ActivityRepository:
    def __init__(self):
        logger.info("Initialising DynamoDB resource")
        try:
            self.db = boto3.resource("dynamodb", region_name='eu-west-1')
        except ClientError as e:
            logger.error(e)

    def insert_activity(self, activity: Activity):
        logger.info(f"Inserting activity for plant {activity.plant_id} into DB")
        try:
            table = self.db.Table("activity")
            table.put_item(Item=asdict(activity))
        except ClientError as e:
            logger.error(e)
            raise

    def select_by_plant_id(self, plant_id: str):
        logger.info(f"Selecting activities for plant id: {plant_id}")
        try:
            table = self.db.Table("activity")
            response = table.query(
                IndexName="plant_id-activity_date-index",
                KeyConditionExpression=Key("plant_id").eq(plant_id),
                FilterExpression=Attr("active").ne(False)
            )
            items = response["Items"]
            logger.info(f"Selected {len(items)}")

            return [
                {k: (list(v) if isinstance(v, set) else v) for k, v in item.items()}
                for item in items
            ]
        except ClientError as e:
            logger.error(e)
            return None

    def select_latest_by_plant_id_and_type(self, plant_id: str, activity_type_id):
        logger.info(f"Selecting latest activity for plant id: {plant_id}, type: {activity_type_id}")
        try:
            table = self.db.Table("activity")
            response = table.query(
                IndexName="plant_id-activity_date-index",
                KeyConditionExpression=Key("plant_id").eq(plant_id),
                FilterExpression=Attr("active").ne(False) & Attr("activity_type_id").eq(activity_type_id),
                ScanIndexForward=False,
                Limit=1
            )
            items = response["Items"]
            if not items:
                return None

            item = items[0]
            return {k: (list(v) if isinstance(v, set) else v) for k, v in item.items()}
        except ClientError as e:
            logger.error(e)
            return None

    def delete_activity_by_id(self, activity_id: str):
        logger.info(f"Deleting activity by id: {activity_id}")
        try:
            table = self.db.Table("activity")
            table.update_item(
                Key={"activity_id": activity_id},
                UpdateExpression="set active = :a",
                ExpressionAttributeValues={
                    ':a': False
                }
            )
        except ClientError as e:
            logger.error(e)
            return {"message": "Activity delete failed"}

        logger.info(f"Deleted {activity_id}")

        return {"message": "Activity deleted successfully"}
