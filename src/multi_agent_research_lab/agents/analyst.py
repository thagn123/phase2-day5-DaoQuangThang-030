"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def __init__(self) -> None:
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""

        prompt = (
            f"Analyze the following research notes. Extract key claims, compare viewpoints, "
            f"and flag any weak evidence or missing points.\n\n"
            f"Query: {state.request.query}\nResearch Notes:\n{state.research_notes}"
        )

        sys_prompt = (
            "You are a data and research analyst. Provide structured insights, "
            "bullet points, and critical analysis."
        )

        response = self.llm_client.complete(
            system_prompt=sys_prompt,
            user_prompt=prompt,
        )

        state.analysis_notes = response.content
        state.agent_results.append(
            AgentResult(
                agent=AgentName(self.name),
                content=response.content,
                metadata={"cost_usd": response.cost_usd},
            )
        )

        return state
