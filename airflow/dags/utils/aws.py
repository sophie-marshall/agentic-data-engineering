import boto3
from botocore.exceptions import BotoCoreError, ClientError
from datetime import datetime
from urllib.parse import quote_plus
import os


class AWSResource:
    def __init__(
        self,
        role_arn: str,
        session_name: str = "agentic_de",
        region_name: str = "us-east-1",
    ):
        self.role_arn = role_arn
        self.session_name = session_name
        self.region_name = region_name
        self._session = None
        self._credentials = None

    def _assume_role(self):
        """Assume an IAM role using AWS Security Token Service (STS)"""
        try:
            sts = boto3.client("sts", region_name=self.region_name)
            assumed_role = sts.assume_role(
                RoleArn=self.role_arn, RoleSessionName=self.session_name
            )
            credentials = assumed_role["Credentials"]
            self._credentials = {
                "aws_access_key_id": credentials["AccessKeyId"],
                "aws_secret_access_key": credentials["SecretAccessKey"],
                "aws_session_token": credentials["SessionToken"],
            }
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"Failed to assume role: {e}")

    def _start_session(self):
        """Start a new Boto3 session using the assumed role credentials"""
        if not self._credentials:
            self._assume_role()

        if not self._session:
            self._session = boto3.Session(
                region_name=self.region_name, **self._credentials
            )


class S3(AWSResource):
    _clients = {}  # map for role arn to a client and session

    def __init__(
        self,
        role_arn: str,
        session_name: str = "agentic_de",
        region_name: str = "us-east-1",
    ):

        super().__init__(
            role_arn, session_name, region_name
        )  # inialize the parent class (AWSResource) with params
        self._s3_client = None

    @classmethod
    def _get_or_create_client(cls, role_arn: str, **kwargs):
        """Get or create an S3 client using the provided role ARN."""

        if role_arn in cls._clients:
            return cls._clients[role_arn][0]

        try:
            aws = AWSResource(role_arn, **kwargs)
            aws._start_session()

            client = aws._session.client("s3")

            cls._clients[role_arn] = (client, aws._session)

            return client
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"Failed to create S3 client: {e}")

    @classmethod
    def upload_raw_rss_data(
        cls, res_dict: dict[str, str] | None, role_arn: str = None, **kwargs
    ):
        if res_dict is None:
            raise ValueError("No data to upload")

        today = datetime.today().strftime("%m%d%Y")

        client = cls._get_or_create_client(role_arn, **kwargs)

        try:
            client.put_object(
                Bucket=os.getenv("S3_BUCKET", "agentic-de"),
                Key=f"bronze/{today}/{quote_plus(res_dict['rss_url'])}_{today}.xml",
                Body=res_dict["xml_doc"],
                ContentType="application/xml",
            )
            print("Success!")
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"Failed to upload to S3: {e}")

    @classmethod
    def get_keys_by_date(cls, date: str, role_arn: str, **kwargs):
        keys = []
        client = cls._get_or_create_client(role_arn, **kwargs)
        paginator = client.get_paginator("list_objects_v2")

        for page in paginator.paginate(
            Bucket=os.getenv("S3_BUCKET"),
            Prefix=f"bronze/{date}",
        ):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                keys.append(key)
        return keys

    @classmethod
    def get_file_metadata(cls, key: str, chars_to_sample: int, role_arn: str, **kwargs):
        client = cls._get_or_create_client(role_arn, **kwargs)
        obj = client.get_object(Bucket=os.getenv("S3_BUCKET"), Key=key)
        content = obj["Body"].read(chars_to_sample).decode("utf-8")
        return f"File: {key}\n Content Preview: \n{content}"
