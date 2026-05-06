"""Researcher agent skeleton."""

import logging

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient

logger = logging.getLogger(__name__)


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self) -> None:
        self.search_client = SearchClient()
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        logger.info(f"Researcher starting search for query: '{state.request.query}'")

        sources = self.search_client.search(
            state.request.query, max_results=state.request.max_sources
        )
        state.sources.extend(sources)
        logger.info(f"Researcher found {len(sources)} sources.")

        # Summarize sources
        snippets = "\n".join([f"- {s.title}: {s.snippet} (URL: {s.url})" for s in sources])
        prompt = (
            f"Summarize these research findings based on the query: '{state.request.query}'. \n\n"
            f"Findings:\n{snippets}"
        )

        response = self.llm_client.complete(
            system_prompt="You are a researcher. Summarize findings accurately with citations.",
            user_prompt=prompt,
        )

        state.research_notes = response.content
        logger.info(
            f"Researcher completed notes (length: {len(state.research_notes)} chars):\n"
            f"{state.research_notes[:200]}..."
        )

        state.agent_results.append(
            AgentResult(
                agent=AgentName(self.name),
                content=response.content,
                metadata={"cost_usd": response.cost_usd, "sources_found": len(sources)},
            )
        )

        return state
