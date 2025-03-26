import boto3
from botocore.exceptions import ClientError
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SecretsManager:
    def __init__(self, region_name):
        self.client = boto3.client('secretsmanager', region_name=region_name)

    def get_secret(self, secret_name):
        try:
            get_secret_value_response = self.client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            logger.error(f"Unable to retrieve secret {secret_name}: {e}")
            raise e
        else:
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
            else:
                secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return json.loads(secret)

    def create_secret(self, name, secret_value):
        try:
            response = self.client.create_secret(
                Name=name,
                SecretString=json.dumps(secret_value)
            )
            logger.info(f"Secret {name} created successfully.")
            return response
        except ClientError as e:
            logger.error(f"Unable to create secret {name}: {e}")
            raise e

    def update_secret(self, secret_name, secret_value):
        try:
            response = self.client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(secret_value)
            )
            logger.info(f"Secret {secret_name} updated successfully.")
            return response
        except ClientError as e:
            logger.error(f"Unable to update secret {secret_name}: {e}")
            raise e

    def delete_secret(self, secret_name, recovery_window_in_days=30):
        try:
            response = self.client.delete_secret(
                SecretId=secret_name,
                RecoveryWindowInDays=recovery_window_in_days
            )
            logger.info(f"Secret {secret_name} scheduled for deletion.")
            return response
        except ClientError as e:
            logger.error(f"Unable to delete secret {secret_name}: {e}")
            raise e