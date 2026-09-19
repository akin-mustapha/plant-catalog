import logging

from repository import ActivityTypeRepository

logger = logging.getLogger()


class ActivityTypeService:
    def __init__(self):
        logger.info("Initialising Activity Type Service")
        self.activity_type_repo = ActivityTypeRepository()

    def get_all(self):
        activity_types = self.activity_type_repo.select_all()
        return activity_types

    def get_activity_type_by_id(self, activity_type_id: int):
        activity_type = self.activity_type_repo.select_by_id(activity_type_id)
        return activity_type
