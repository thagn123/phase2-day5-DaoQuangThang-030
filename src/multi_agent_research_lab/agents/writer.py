"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self) -> None:
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""

        prompt = (
            "Write a comprehensive final answer for the user based on the "
            "research and analysis notes.\n\n"
            f"Query: {state.request.query}\nAudience: {state.request.audience}\n\n"
            f"Research Notes:\n{state.research_notes}\n\n"
            f"Analysis Notes:\n{state.analysis_notes}\n\n"
            "Ensure you synthesize a clear response with citations."
        )

        sys_prompt = (
            "You are an expert technical writer. Write clearly, structure logically, "
            "and use Markdown. Always cite sources."
        )

        response = self.llm_client.complete(
            system_prompt=sys_prompt,
            user_prompt=prompt,
        )

        state.final_answer = response.content
        state.agent_results.append(
            AgentResult(
                agent=AgentName(self.name),
                content=response.content,
                metadata={"cost_usd": response.cost_usd},
            )
        )

        return state
