import logging
import boto3
from botocore.exceptions import ClientError


class EmailClient:
    def __init__(self):
        self.ses_client = boto3.client("ses", region_name="eu-west-1")
        self.logger = logging.getLogger(__name__)
    def send_email(self, recipient: str, subject: str, body: str):
        # Implement the logic to send an email using an email service provider
        # For example, you can use AWS SES, SendGrid, or any other email service
        # Here, we'll just log the email details for demonstration purposes
        self.logger.info(f"Sending email to {recipient} with subject '{subject}' and body '{body}'")