import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from .tools.sandbox_tools import sandbox_tools, test_agent_tools
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class EngineeringTeam():
    """EngineeringTeam crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @property
    def gemini_llm(self):
        return LLM(
            model="gemini/gemini-3.1-flash-lite",
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=1.0,
            verbose=True
        )

    @agent
    def engineering_lead(self) -> Agent:
        return Agent(
            config=self.agents_config['engineering_lead'],
            verbose=True,
            mcps=["https://mcp.context7.com/mcp"],
            llm=self.gemini_llm,
            max_iter=6,
            max_retry_limit=2
        )

    @agent
    def backend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['backend_engineer'],
            verbose=True,
            tools=sandbox_tools,
            llm=self.gemini_llm,
            max_iter=6,
            max_retry_limit=2
        )
    
    @agent
    def frontend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['frontend_engineer'],
            verbose=True,
            tools=sandbox_tools,
            mcps=["https://mcp.context7.com/mcp"],
            llm=self.gemini_llm,
            max_iter=6,
            max_retry_limit=2
        )
    
    @agent
    def test_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['test_engineer'],
            verbose=True,
            tools=test_agent_tools,
            llm=self.gemini_llm,
            max_iter=6,
            max_retry_limit=2
        )

    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config['design_task']
        )

    @task
    def code_task(self) -> Task:
        return Task(
            config=self.tasks_config['code_task'],
        )

    @task
    def frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config['frontend_task'],
        )

    @task
    def test_task(self) -> Task:
        return Task(
            config=self.tasks_config['test_task'],
        )   

    @crew
    def crew(self) -> Crew:
        """Creates the EngineeringTeam crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            tracing=True
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )