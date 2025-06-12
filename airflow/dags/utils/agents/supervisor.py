from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentType


from airflow.dags.utils.airflow_client import AirflowClient


class SupervisorAgent:

    # class vars
    _agent = None
    _llm = None

    @classmethod
    def _instantiate_agent(cls):
        """
        Instantiate the Supervisor Agent with the necessary tools and configuration.
        """

        if cls._agent is not None:
            return cls._agent

        # define toolset available to our Agent
        tools = [
            Tool(
                name="TriggerTransformationDAG",
                func=lambda dag_id: AirflowClient.trigger_dag(dag_id=dag_id),
                description="Trigger an Airflow DAG. The DAG is specified by its ID.",
            )
        ]

        # configure agent with laguage model etc.
        cls._llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
        )

        # make the agent
        cls._agent = initialize_agent(
            tools=tools,
            llm=cls._llm,
            init_agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
        )

        return cls._agent

    @classmethod
    def trigger(cls, metadata: str):

        if not cls._agent:
            cls._instantiate_agent()

        prompt = f"""
            You are a supervisor agent. Your task is to examine the file content and decide which Airflow DAG should be triggered.

            Here is the metadata:
            {metadata}

            Choose the correct DAG ID from:
            - transform_pbs_data
            - transform_npr_data

            Then call TriggerTrasnformationDAG with the correct DAG ID.
        """

        print(cls._agent.run(prompt))
