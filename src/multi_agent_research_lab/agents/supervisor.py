"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""

        # Enforce max iterations
        if state.iteration >= 5:
            state.errors.append("Max iterations reached in Supervisor")
            state.route_history.append("done")
            return state

        next_agent = ""
        if not state.research_notes:
            next_agent = "researcher"
        elif not state.analysis_notes:
            next_agent = "analyst"
        elif not state.final_answer:
            next_agent = "writer"
        else:
            # We can run critic here to validate final answer.
            next_agent = "critic" if "critic" not in state.route_history else "done"

        state.record_route(next_agent)
        state.agent_results.append(
            AgentResult(
                agent=AgentName(self.name),
                content=f"Routed to {next_agent}",
                metadata={"next": next_agent},
            )
        )

        return state
