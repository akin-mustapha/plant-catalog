import logging

from models import Activity
from repository import ActivityRepository

logger = logging.getLogger()


class ActivityService:
    def __init__(self):
        logger.info("Initialising Activity Service")
        self.activity_repo = ActivityRepository()

    def add_activity(self, activity: Activity):
        self.activity_repo.insert_activity(activity)
        return {"message": "Activity added successfully"}

    def get_by_plant_id(self, plant_id: str):
        activities = self.activity_repo.select_by_plant_id(plant_id)
        return activities

    def delete_activity_by_id(self, activity_id: str):
        delete_result = self.activity_repo.delete_activity_by_id(activity_id)
        return delete_result
