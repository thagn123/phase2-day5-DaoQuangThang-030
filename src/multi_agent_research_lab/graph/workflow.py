"""LangGraph workflow skeleton."""

from typing import Any, cast

from langgraph.graph import END, StateGraph

from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.critic import CriticAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.core.state import ResearchState


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph."""

    def __init__(self) -> None:
        self.supervisor = SupervisorAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
        self.critic = CriticAgent()

    def build(self) -> Any:
        """Create a LangGraph graph."""
        workflow = StateGraph(ResearchState)

        workflow.add_node("supervisor", self.supervisor.run)
        workflow.add_node("researcher", self.researcher.run)
        workflow.add_node("analyst", self.analyst.run)
        workflow.add_node("writer", self.writer.run)
        workflow.add_node("critic", self.critic.run)

        workflow.set_entry_point("supervisor")

        def route_from_supervisor(state: ResearchState) -> str:
            if not state.route_history:
                return END
            last_route = state.route_history[-1]
            if last_route == "done":
                return END
            return last_route

        workflow.add_conditional_edges("supervisor", route_from_supervisor)
        workflow.add_edge("researcher", "supervisor")
        workflow.add_edge("analyst", "supervisor")
        workflow.add_edge("writer", "supervisor")
        workflow.add_edge("critic", "supervisor")

        self.app = workflow.compile()
        return self.app

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""
        if not hasattr(self, "app"):
            self.build()
        # LangGraph invoke takes a dict and returns a dict for pydantic models
        # in StateGraph depending on version
        # If StateGraph uses the class directly it might return the class instance
        result = self.app.invoke(state)
        if isinstance(result, dict):
            return ResearchState(**result)
        return cast(ResearchState, result)
