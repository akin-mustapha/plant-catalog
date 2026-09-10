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
