import logging
import uuid
from dataclasses import asdict

from models import Notification, Contact, NotificationContact
from repository import NotificationRepository

logger = logging.getLogger()

MAX_CONTACTS = 3


class NotificationService:
    def __init__(self):
        logger.info("Initialising Notification Service")
        self.notification_repo = NotificationRepository()

    def create_notification(self, notification: Notification):
        
        self.validate_notification(notification)
        
        self.notification_repo.insert_notification(notification)
        
        for contact in notification.contacts or []:
            contact = Contact(
                contact_id=contact.get("contact_id", str(uuid.uuid4())),
                notification_id=notification.notification_id,
                name=contact.get("name"),
                email=contact.get("email"),
                phone_number=contact.get("phone_number"),
                created=contact.get("created"),
                active=contact.get("active", True)
            )
            self.notification_repo.insert_contact(contact)
            notification_contact = NotificationContact(
                notification_id=notification.notification_id,
                contact_id=contact.contact_id
            )
            self.notification_repo.insert_notification_contact(notification_contact)
        
        return asdict(notification)

    def get_plant_notification(self, plant_id: str):
        return self.notification_repo.select_by_plant_id(plant_id)

    def get_all(self):
        return self.notification_repo.select_all()

    def get_notification_by_id(self, notification_id: str):
        return self.notification_repo.select_by_id(notification_id)

    def update_notification(self, notification_id: str, notification: Notification):
        self.validate_notification(notification)
        return self.notification_repo.update_notification_by_id(notification_id, notification)

    def delete_notification(self, notification_id: str):
        return self.notification_repo.delete_by_id(notification_id)

    def validate_notification(self, notification: Notification):
        if len(notification.contacts or []) > MAX_CONTACTS:
            raise ValueError(f"A notification supports at most {MAX_CONTACTS} contacts")

        if bool(notification.schedule) == bool(notification.interval):
            raise ValueError("Exactly one of schedule or interval must be set")

    def subscribe_contact(self, topic_arn: str, email: str):
        pass

    def unsubscribe_contact(self, subscription_arn: str):
        pass
