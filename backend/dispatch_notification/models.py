from dataclasses import dataclass


@dataclass
class NotificationLog:
    notification_id: str
    sent_at: str

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


