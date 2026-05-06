"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass

from openai import OpenAI

from multi_agent_research_lab.core.config import get_settings


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client skeleton."""

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion."""
        settings = get_settings()
        api_key = settings.openai_api_key or "dummy_key"
        client = OpenAI(api_key=api_key)
        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content or ""
            usage = response.usage
            if usage:
                cost = (usage.prompt_tokens / 1_000_000) * 0.150 + (
                    usage.completion_tokens / 1_000_000
                ) * 0.600
                return LLMResponse(
                    content=content,
                    input_tokens=usage.prompt_tokens,
                    output_tokens=usage.completion_tokens,
                    cost_usd=cost,
                )
            return LLMResponse(content=content)
        except Exception as e:
            return LLMResponse(content=f"Error: {e}")
