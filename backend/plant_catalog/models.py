from dataclasses import dataclass


@dataclass
class Plant:
    plant_id: str
    common_name: str
    nick_name: str
    scientific_name: str
    notes: str
    date_acquired: str
    location: str
    status: str
    routine: dict
    preference: dict
    active: bool


@dataclass
class Activity:
    activity_id: str
    plant_id: str
    activity_type_id: str
    activity_date: str
    notes: str
    created: str
    active: bool


@dataclass
class ActivityType:
    activity_type_id: str
    description: str
    created: str
    active: bool


@dataclass
class Notification:
    notification_id: str
    plant_id: str
    type_id: str
    name: str
    description: str
    status: str
    contacts: list
    user_id: str = None
    schedule: str = None
    interval: str = None
    next_run_date: str = None
    topic_arn: str = None


@dataclass
class Contact:
    contact_id: str
    notification_id: str
    name: str
    email: str
    phone_number: str
    created: str
    active: bool


@dataclass
class NotificationContact:
    notification_id: str
    contact_id: str

