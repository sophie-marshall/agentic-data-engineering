from airflow.sdk import dag, task, Variable


@dag(schedule=None, tags=["agentic-de"])
def transform_pbs_data():
    """
    This DAG is responsible for transforming the NPR data.
    """

    @task()
    def transform_pbs():
        """
        Transform the PBS data.
        """
        return {"message": "This worked!"}

    transform_pbs()


transform_pbs_data()
