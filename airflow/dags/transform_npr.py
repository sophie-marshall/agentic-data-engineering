from airflow.sdk import dag, task, Variable


@dag(schedule=None, tags=["agentic-de"])
def transform_npr_data():
    """
    This DAG is responsible for transforming the NPR data.
    """

    @task()
    def transform_npr():
        """
        Transform the NPR data.
        """
        return {"message": "This worked!"}

    transform_npr()


transform_npr_data()
