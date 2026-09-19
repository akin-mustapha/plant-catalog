import logging

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

logger = logging.getLogger()


class ActivityTypeRepository:
    def __init__(self):
        logger.info("Initialising DynamoDB resource")
        try:
            self.db = boto3.resource("dynamodb", region_name='eu-west-1')
        except ClientError as e:
            logger.error(e)

    def select_all(self):
        logger.info("Selecting all activity types")
        try:
            table = self.db.Table("activity_type")
            response = table.scan(
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

    def select_by_id(self, activity_type_id: int):
        logger.info(f"Selecting activity type by id: {activity_type_id}")
        try:
            table = self.db.Table("activity_type")
            response = table.get_item(Key={"activity_type_id": activity_type_id})

            item = response.get("Item")
            if item is None or item.get("active") is False:
                logger.info(f"No active activity type found for id: {activity_type_id}")
                return None

            logger.info(f"Selected {len(item)}")

            return {k: (list(v) if isinstance(v, set) else v) for k, v in item.items()}
        except ClientError as e:
            logger.error(e)
            return None
