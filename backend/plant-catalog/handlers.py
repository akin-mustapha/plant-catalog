import json
import logging
import uuid
from datetime import datetime, timezone

from models import Plant, Activity
from routes import route
from service import PlantService, ActivityService, ActivityTypeService
from responses import json_response

logger = logging.getLogger()


# ========================
# API
# ========================

@route("POST", "/plants")
def create_plant(event):
    body = json.loads(event["body"])

    logger.info(f'Create plant - {body.get("common_name")}')
    plant = Plant(
        plant_id=str(uuid.uuid4()),
        active=True,
        **body
    )

    created_plant = PlantService().add_plant(plant)

    logger.info(f"Plant created - {plant.plant_id}")
    return json_response(201, created_plant)

@route("GET", "/plants")
def get_all_plants(event):
    logger.info("Getting all plants")
    plants = PlantService().get_all()

    logger.info(f"Fetched {len(plants)} plant(s)")
    return json_response(200, plants)

@route("GET", "/plants/{id}")
def get_plant_by_id(event):
    plant_id = event['pathParameters']['id']

    logger.info(f"Getting plant by id {plant_id}")
    plant = PlantService().get_plant_by_id(plant_id)

    if plant is None:
        return json_response(404, {"message": "Plant not found"})

    return json_response(200, plant)

@route("PUT", "/plants/{id}")
def update_plant_by_id(event):
    body = json.loads(event["body"])
    plant_id = event["pathParameters"]["id"]

    logger.info(f"Updating plant by id {plant_id}")

    plant = Plant(plant_id=plant_id, active=True, **{
        k: v for k, v in body.items() if k not in ("plant_id", "active")
    })

    update_result = PlantService().update_plant_by_id(plant_id, plant)
    logger.info("Updated a plant")
    return json_response(201, update_result)

@route("DELETE", "/plants/{id}")
def delete_plant_by_id(event):
    plant_id = event['pathParameters']['id']

    logger.info(f"Deleting plant by id {plant_id}")

    delete_result = PlantService().delete_plant_by_id(plant_id)

    logger.info("Deleted a plant")

    return json_response(200, delete_result)

@route("POST", "/plants/{id}/image/upload-url")
def request_plant_image_upload_url(event):
    body = json.loads(event["body"])

    logger.info(f"Uploading image for plant {body['plant_id']}")

    plant_service = PlantService()

    plant_id = body.get("plant_id", None)
    file_name = body.get("file_name", None)
    content_type = body.get("content_type") or "image/jpeg"

    upload_url = plant_service.generate_plant_image_upload_url(plant_id, file_name, content_type)

    return json_response(200, upload_url, extra_headers={"Content-Type": "application/json"})

@route("POST", "/plants/{id}/image/confirm")
def confirm_plant_image_upload(event):

    body = json.loads(event["body"])

    plant_service = PlantService()

    confirmation = plant_service.confirm_plant_image_upload(body)

    return json_response(200, confirmation, extra_headers={"Content-Type": "application/json"})

@route("POST", "/plants/{id}/activities")
def create_activity(event):
    body = json.loads(event["body"])
    plant_id = event["pathParameters"]["id"]
    now = datetime.now(timezone.utc).isoformat()

    logger.info(f"Create activity for plant {plant_id}")
    activity = Activity(
        activity_id=str(uuid.uuid4()),
        plant_id=plant_id,
        notes=body.get("notes", ""),
        activity_type_id=body["activity_type_id"],
        activity_date=body.get("activity_date", now),
        created=now,
        active=True
    )

    created_activity = ActivityService().add_activity(activity)

    logger.info(f"Activity created - {activity.activity_id}")
    return json_response(201, created_activity)

@route("GET", "/plants/{id}/activities")
def get_activities_by_plant_id(event):
    plant_id = event["pathParameters"]["id"]

    logger.info(f"Getting activities for plant {plant_id}")
    activities = ActivityService().get_by_plant_id(plant_id)

    logger.info(f"Fetched {len(activities)} activity(ies)")
    return json_response(200, activities)

@route("DELETE", "/plants/{id}/activities/{activityId}")
def delete_activity_by_id(event):
    activity_id = event["pathParameters"]["activityId"]

    logger.info(f"Deleting activity by id {activity_id}")

    delete_result = ActivityService().delete_activity_by_id(activity_id)

    logger.info("Deleted an activity")

    return json_response(200, delete_result)

@route("GET", "/activity-types")
def get_all_activity_types(event):
    logger.info("Getting all activity types")
    activity_types = ActivityTypeService().get_all()

    logger.info(f"Fetched {len(activity_types)} activity type(s)")
    return json_response(200, activity_types)
