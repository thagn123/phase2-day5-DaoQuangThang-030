"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def __init__(self) -> None:
        self.llm_client = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""

        prompt = (
            f"Critique the following answer. Check for hallucinations, citation coverage, "
            f"and logic gaps.\n\nQuery: {state.request.query}\nAnswer:\n{state.final_answer}\n\n"
            f"Provide your feedback concisely."
        )

        sys_prompt = (
            "You are a strict technical critic. Verify facts, identify hallucinations, "
            "and evaluate completeness."
        )

        response = self.llm_client.complete(
            system_prompt=sys_prompt,
            user_prompt=prompt,
        )

        # We append the critique to the agent results.
        # If we were optimizing, we would loop back to Writer.
        # But we'll just store the critique in the state.
        state.agent_results.append(
            AgentResult(
                agent=AgentName(self.name),
                content=response.content,
                metadata={"cost_usd": response.cost_usd},
            )
        )

        return state
