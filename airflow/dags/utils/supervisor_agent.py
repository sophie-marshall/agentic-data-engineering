from langchain.agents import init_agent, Tool

from airflow_client import AirflowClient


class SupervisorAgent:

    # define toolset available to our Agent
    tools = [
        Tool(
            name="TriggerTransformationDAG",
            func=lambda dag_id: AirflowClient.trigger_dag(dag_id=dag_id),
            description="Trigger an Airflow DAG. The DAG is specified by its ID.",
        )
    ]

    # configure agent with laguage model etc.
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
    )
