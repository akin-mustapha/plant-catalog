import boto3
from botocore.exceptions import ClientError
from models import NotificationLog
from repository import NotificationRepositoryFactory


class NotificationDispatchService:
    def __init__(self):
        self.notification_repo = NotificationRepositoryFactory.get("prod")
        self.ses_client = boto3.client("ses", region_name="eu-west-1")

    def send_notifications(self):
        notifications = self.notification_repo.select_all()
        for notification in notifications:
            if notification.get("status").lower() == "active":
              contacts = notification.get("contacts", [])
              for contact in contacts:
                    email = contact.get("email")
                    print("Sending email to: ", email)
                    self.ses_client.send_email(
                      Source="akinkunmimustapha1@gmail.com",
                      Destination={
                          "ToAddresses": [email]
                      },
                      Message={
                          "Subject": {
                              "Data": "Plant Catalog Notification"
                          },
                          "Body": {
                              "Text": {
                                  "Data": "https://main.d2dl67h6vhyf6v.amplifyapp.com/index.html"
                              }
                          }
                      }
                    )
                    
              notification_log = NotificationLog(
                    notification_id=notification.get("notification_id"),
                    sent_at="2023-08-01T12:00:00Z"  # Replace with actual timestamp
                )
              self.notification_repo.insert_notification_log(notification_log)

if __name__ == "__main__":
    service = NotificationDispatchService()
    service.send_notifications()