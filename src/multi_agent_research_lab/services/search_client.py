"""Search client abstraction for ResearcherAgent."""

import json
import urllib.request

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""

        settings = get_settings()
        tavily_api_key = settings.tavily_api_key
        if tavily_api_key:
            data = {"query": query, "api_key": tavily_api_key, "max_results": max_results}
            req = urllib.request.Request(
                "https://api.tavily.com/search",
                json.dumps(data).encode(),
                {"Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(req) as response:
                    res = json.loads(response.read())
                    return [
                        SourceDocument(
                            title=r.get("title", ""),
                            url=r.get("url", ""),
                            snippet=r.get("content", ""),
                        )
                        for r in res.get("results", [])
                    ]
            except Exception:
                pass

        # Fallback Mock
        return [
            SourceDocument(
                title="GraphRAG Overview",
                url="https://example.com/graphrag",
                snippet=(
                    "GraphRAG combines knowledge graphs with Retrieval-Augmented Generation "
                    "to improve global reasoning over large document collections. It extracts "
                    "entities and relationships to build a graph, then creates community summaries."
                ),
            ),
            SourceDocument(
                title="Multi-Agent Systems",
                url="https://example.com/mas",
                snippet=(
                    "Multi-agent systems utilize multiple AI agents to collaborate "
                    "on complex tasks. Key patterns include Supervisor, Routing, "
                    "and Parallel execution. It is crucial to have guardrails like "
                    "max iterations."
                ),
            ),
        ]
