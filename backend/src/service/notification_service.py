import logging

from repository import NotificationRepository

logger = logging.getLogger()


class NotificationService:
    def __init__(self):
        logger.info("Initialising Notification Service")
        self.notification_repo = NotificationRepository()

    def create_notification(self, notification):
        pass

    def get_notification(self, user_id: str):
        pass

    def update_notification(self, notification_id: str, notification):
        pass

    def validate_notification(self, notification):
        pass

    def subscribe_contact(self, topic_arn: str, email: str):
        pass

    def unsubscribe_contact(self, subscription_arn: str):
        pass
