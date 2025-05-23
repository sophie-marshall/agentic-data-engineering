import requests
from datetime import datetime, timezone


class AirflowClient:
    def __init__(
        self, username: str, password: str, endpoint_url: str = "http://localhost:8080"
    ):
        self.username = username
        self.password = password
        self.endpoint_url = endpoint_url
        self.auth_token = self._get_auth_token()

    def _get_auth_token(self):
        res = requests.post(
            url=f"{self.endpoint_url}/auth/token",
            headers={"Content-Type": "application/json"},
            json={"username": self.username, "password": self.password},
        )

        return res.json()["access_token"]

    def trigger_dag(self, dag_id: str):
        # set date
        logical_date = datetime.now(timezone.utc).isoformat()
        dag_run_id = f"manual__{logical_date}"

        # trigger DAG
        res = requests.post(
            url=f"{self.endpoint_url}/api/v2/dags/{dag_id}/dagRuns",
            headers={
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json",
            },
            json={
                "dag_run_id": dag_run_id,
                "logical_date": logical_date,
            },
        )

        return {"status_code": res.status_code, "response": res.json()}
