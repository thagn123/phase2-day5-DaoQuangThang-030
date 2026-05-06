"""Benchmark skeleton for single-agent vs multi-agent."""

from collections.abc import Callable
from time import perf_counter

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState

Runner = Callable[[str], ResearchState]


def run_benchmark(
    run_name: str, query: str, runner: Runner
) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return a placeholder metric object."""

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started

    cost = 0.0
    for res in state.agent_results:
        if res.metadata and "cost_usd" in res.metadata and res.metadata["cost_usd"]:
            cost += res.metadata["cost_usd"]

    # Simple quality score based on having a final answer
    quality = 0.0
    if state.final_answer:
        quality = 8.0  # dummy score, ideally use LLM as judge
        if len(state.final_answer) > 200:
            quality = 9.0

    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=cost,
        quality_score=quality,
        notes="Automated benchmark run",
    )
    return state, metrics
