import logging
from dataclasses import asdict

import boto3
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

from models import Plant, Activity

logger = logging.getLogger()


class PlantRepository:
    def __init__(self):
        logger.info("Initialising DynamoDB resource")
        try:
            self.db = boto3.resource("dynamodb", region_name='eu-west-1')
        except ClientError as e:
            logger.error(e)

    def insert_plant(self, plant: Plant):
        logger.info(f"Inserting {plant.common_name} into DB")
        try:
            table = self.db.Table("plants")
            table.put_item(Item=asdict(plant))
        except ClientError as e:
            logger.error(e)
            raise

    def select_all(self):
        logger.info("Selecting all plants")
        try:
            table = self.db.Table("plants")
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

    def select_by_id(self, plant_id: str):
        logger.info(f"Selecting plant by id: {plant_id}")
        try:
            table = self.db.Table("plants")
            response = table.get_item(Key={"plant_id": plant_id})

            item = response.get("Item")
            if item is None or item.get("active") is False:
                logger.info(f"No active plant found for id: {plant_id}")
                return None

            logger.info(f"Selected {len(item)}")

            return {k: (list(v) if isinstance(v, set) else v) for k, v in item.items()}
        except ClientError as e:
            logger.error(e)
            return None

    def delete_by_id(self, plant_id: str):
        logger.info(f"Deleting plant by id: {plant_id}")
        # hard delete
        try:
            table = self.db.Table("plants")
            response = table.update_item(
                Key={"plant_id": plant_id},
                UpdateExpression="set active = :a",
                ExpressionAttributeValues={
                    ':a': False
                }
            )
        except ClientError as e:
            logger.error(e)

        logger.info(f"Deleted {plant_id}")

        return {"message": "Plant deleted successfully"}

    def update_plant_by_id(self, plant_id: str, plant: Plant):
        logger.info(f"Updating plant by id: {plant_id}")
        try:
            table = self.db.Table("plants")
            table.update_item(
                Key={
                    "plant_id": plant_id
                },
                UpdateExpression="""
                    set #cn=:cn,
                    #nn=:nn,
                    #sn=:sn,
                    #n=:n,
                    #da=:da,
                    #loc=:l,
                    #st=:s,
                    #r=:r,
                    #p=:p,
                    #a=:a
                """,
                ExpressionAttributeNames={
                    "#cn": "common_name",
                    "#nn": "nick_name",
                    "#sn": "scientific_name",
                    "#n": "notes",
                    "#da": "date_acquired",
                    "#loc": "location",
                    "#st": "status",
                    "#r": "routine",
                    "#p": "preference",
                    "#a": "active"
                },
                ExpressionAttributeValues={
                    ":cn": plant.common_name,
                    ":nn": plant.nick_name,
                    ":sn": plant.scientific_name,
                    ":n": plant.notes,
                    ":da": plant.date_acquired,
                    ":l": plant.location,
                    ":s": plant.status,
                    ":r": plant.routine,
                    ":p": plant.preference,
                    ":a": plant.active
                },
                ConditionExpression=Attr("active").eq(True)
            )
        except ClientError as e:
            logger.error(e)
            return {"message": "Plant update failed"}

        logger.info(f"Updated {plant_id}")

        return {"message": "Plant updated successfully"}

    def update_plant_image_url(self, plant_id: str, image_url: str):
        logger.info(f"Updating image url for plant: {plant_id}")
        try:
            table = self.db.Table("plants")
            table.update_item(
                Key={
                    "plant_id": plant_id
                },
                UpdateExpression="set image_url=:i",
                ExpressionAttributeValues={
                    ":i": image_url
                },
                ConditionExpression=Attr("active").eq(True)
            )
        except ClientError as e:
            logger.error(e)
            return {"message": "Plant image url update failed"}

        logger.info(f"Updated image url for {plant_id}")

        return {"message": "Plant image url updated successfully"}


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
