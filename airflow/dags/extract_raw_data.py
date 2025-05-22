import pendulum
import requests
import boto3
from datetime import datetime
from urllib.parse import quote_plus

from airflow.sdk import dag, task, Variable


def get_s3_client_with_role(role_arn: str, region: str = "us-east-1"):
    sts = boto3.client("sts")
    creds = sts.assume_role(RoleArn=role_arn, RoleSessionName="airflow-dag-session")[
        "Credentials"
    ]

    return boto3.client(
        "s3",
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=region,
    )


@dag(
    schedule=None,
    start_date=pendulum.datetime(2025, 5, 22, tz="UTC"),
    catchup=False,
    tags=["agentic-de"],
)
def extract_raw_data():
    @task()
    def request_feed(rss_feed_url: str) -> dict[str, str] | None:
        res = requests.get(rss_feed_url, timeout=10)
        if res.status_code != 200:
            print(
                f"Error retrieving XML document for {rss_feed_url}: {res.status_code}"
            )
            return None

        return {
            "rss_url": rss_feed_url,
            "xml_doc": res.text,
        }

    @task()
    def upload_to_bronze(res_dict: dict[str, str] | None) -> None:
        if res_dict is None:
            print("No data to upload")
            return

        today = datetime.today().strftime("%m%d%Y")
        role_arn = Variable.get("DIGI_INNO_ROLE_ARN")
        if not role_arn:
            print("Missing role ARN")
            return

        s3 = get_s3_client_with_role(role_arn)
        try:
            s3.put_object(
                Bucket="agentic-de",
                Key=f"bronze/{today}/{quote_plus(res_dict['rss_url'])}_{today}.xml",
                Body=res_dict["xml_doc"],
                ContentType="application/xml",
            )
            print("Success!")
        except Exception as e:
            print(f"Error uploading to S3: {str(e)}")

    xml_docs = request_feed.expand(rss_feed_url=FEED_URLS)
    upload_to_bronze.expand(res_dict=xml_docs)


extract_raw_data()
