import logging
from dataclasses import asdict

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from models import Plant

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
