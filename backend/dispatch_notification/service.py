import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import json
from repository import NotificationRepositoryFactory

ses_client = boto3.client("ses", region_name="eu-west-1")

notification_repo = NotificationRepositoryFactory.get("prod")

notification = notification_repo.select_all()
# DECLARE mailing_list
# FOR ALL notification

for notification in notification:
    if notification.get("status").lower() == "active":
        contacts = notification.get("contacts", [])
        for contact in contacts:
          email = contact.get("email")
          print("Sending email to: ", email)
          ses_client.send_email(
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

#.  FOR ALL notification.contacts
# IF Active = True
# ADD contact to mailing_list


# DECLARE ses_client
# FO