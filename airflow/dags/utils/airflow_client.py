import requests
from datetime import datetime, timezone
import os


class AirflowClient:

    _username = os.getenv("AIRFLOW_USER")
    _password = os.getenv("AIRFLOW_PASSWORD")
    _endpoint = os.getenv("AIRFLOW_ENDPOINT")
    _auth_token = None

    @classmethod
    def _get_auth_token(cls):
        try:
            res = requests.post(
                url=f"{cls._endpoint}/auth/token",
                headers={"Content-Type": "application/json"},
                json={"username": cls._username, "password": cls._password},
            )

            cls._auth_token = res.json()["access_token"]
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get auth token: {e}")

    @classmethod
    def trigger_dag(cls, dag_id: str):
        if not cls._auth_token:
            cls._get_auth_token()

        # set date
        logical_date = datetime.now(timezone.utc).isoformat()
        dag_run_id = f"manual__{logical_date}"

        # trigger DAG
        res = requests.post(
            url=f"{cls._endpoint}/api/v2/dags/{dag_id}/dagRuns",
            headers={
                "Authorization": f"Bearer {cls._auth_token}",
                "Content-Type": "application/json",
            },
            json={
                "dag_run_id": dag_run_id,
                "logical_date": logical_date,
            },
        )

        return {"status_code": res.status_code, "response": res.json()}
