import logging
import uuid

import boto3
from botocore.exceptions import ClientError

from models import Plant
from repository import PlantRepository, ActivityRepository, ActivityTypeRepository

logger = logging.getLogger()


class PlantService:
    def __init__(self):

        logger.info("Initialising Plant Service")
        self.plant_repo = PlantRepository()
        self.activity_repo = ActivityRepository()
        self.activity_type_repo = ActivityTypeRepository()


        self.plant_bucket="plant-app-images-eu-west-1"
        self.s3_client = boto3.client(
            's3',
            region_name='eu-west-1',
            endpoint_url='https://s3.eu-west-1.amazonaws.com'
        )

    def add_plant(self, plant: Plant):
        self.plant_repo.insert_plant(plant)
        return {"message": "Plant added successfully"}

    def get_all(self):
        plants = self.plant_repo.select_all()

        watering_type_id = self._get_watering_type_id()
        if watering_type_id is not None:
            for plant in plants:
                latest_watering = self.activity_repo.select_latest_by_plant_id_and_type(
                    plant["plant_id"], watering_type_id
                )
                plant["last_watered"] = latest_watering["activity_date"] if latest_watering else None

        return plants

    def _get_watering_type_id(self):
        activity_types = self.activity_type_repo.select_all() or []
        watering_type = next(
            (t for t in activity_types if t.get("description") == "Watering"), None
        )
        return watering_type["activity_type_id"] if watering_type else None

    def get_plant_by_id(self, plant_id: str):
        plant = self.plant_repo.select_by_id(plant_id)
        return plant

    def update_plant_by_id(self, plant_id: str, plant: Plant):
        update_result = self.plant_repo.update_plant_by_id(plant_id, plant)
        return update_result

    def delete_plant_by_id(self, plant_id: str):
        delete_result = self.plant_repo.delete_by_id(plant_id)

        return delete_result

    def generate_plant_image_upload_url(self, plant_id: str, file_name: str, content_type: str = "image/jpeg"):
        key = f"uploads/{uuid.uuid4()}-{file_name}"

        presigned_url = self.s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": self.plant_bucket,
                "Key": key,
                "ContentType": content_type
            },
            ExpiresIn=300  # 5 minutes
        )

        return {"uploadUrl": presigned_url, "key": key}

    def confirm_plant_image_upload(self, body: dict):
        plant_id = body.get("plant_id", None)
        key = body.get("key", None)

        try:
            image_url = f"https://{self.plant_bucket}.s3.amazonaws.com/{key}"

            self.plant_repo.update_plant_image_url(plant_id, image_url)

        except ClientError as e:
            logger.error(e)
            return {"message": "Image upload confirmation failed"}

        return {"message": "Image uploaded", "image_url": image_url}
