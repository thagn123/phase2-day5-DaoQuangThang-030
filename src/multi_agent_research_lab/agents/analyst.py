"""Analyst agent skeleton."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient

logger = logging.getLogger(__name__)


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def __init__(self) -> None:
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        logger.info("Analyst starting to process research notes.")

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
        logger.info(
            f"Analyst completed analysis (length: {len(state.analysis_notes)} chars):\n"
            f"{state.analysis_notes[:200]}..."
        )

        state.agent_results.append(
            AgentResult(
                agent=AgentName(self.name),
                content=response.content,
                metadata={"cost_usd": response.cost_usd},
            )
        )

        return state
