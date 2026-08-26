"""Provider protocol and DI helper."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol, TypedDict


class AdviceItem(TypedDict):
    title: str
    detail: str
    confidence: float  # 0.0 - 1.0


class AdviceResult(TypedDict):
    provider: str
    model: str
    content: list[AdviceItem]
    generated_at: str  # ISO 8601


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def empty_result(provider: str, model: str) -> AdviceResult:
    return AdviceResult(
        provider=provider,
        model=model,
        content=[],
        generated_at=_now_iso(),
    )


class StartupAdvisorProvider(Protocol):
    """Strategy interface for startup advice.

    All methods are ``async`` to match the shape of real network-backed
    providers without leaking the abstraction to the routers.
    """

    name: str

    async def validate(self, idea: dict[str, Any]) -> AdviceResult: ...
    async def swot_suggestions(self, idea: dict[str, Any]) -> AdviceResult: ...
    async def risk_suggestions(self, idea: dict[str, Any]) -> AdviceResult: ...
    async def competitor_recommendations(
        self, idea: dict[str, Any], market: str | None
    ) -> AdviceResult: ...
    async def growth_roadmap(self, idea: dict[str, Any]) -> AdviceResult: ...


# Lazy singleton ---------------------------------------------------------

_provider: StartupAdvisorProvider | None = None


def get_advisor_provider() -> StartupAdvisorProvider:
    """Return the configured provider (instantiated once per process)."""
    global _provider
    if _provider is None:
        from app.ai.mock import MockStartupAdvisorProvider
        from app.core.config import get_settings

        settings = get_settings()
        if settings.startup_advisor_provider != "mock":
            # All non-mock providers are stubs in v1. We still want DI to
            # succeed so the rest of the app boots; the provider itself
            # raises NotConfiguredError when used.
            from app.ai import claude as claude_mod
            from app.ai import gemini as gemini_mod
            from app.ai import groq as groq_mod
            from app.ai import ollama as ollama_mod
            from app.ai import openai as openai_mod

            table = {
                "openai": openai_mod.OpenAIProvider,
                "gemini": gemini_mod.GeminiProvider,
                "claude": claude_mod.ClaudeProvider,
                "groq": groq_mod.GroqProvider,
                "ollama": ollama_mod.OllamaProvider,
            }
            cls = table.get(settings.startup_advisor_provider)
            _provider = (
                MockStartupAdvisorProvider(settings.ai_data_dir)
                if cls is None
                else cls()  # type: ignore[abstract]
            )
        else:
            _provider = MockStartupAdvisorProvider(settings.ai_data_dir)
    return _provider


def reset_provider_cache() -> None:
    """Test helper — clears the cached provider."""
    global _provider
    _provider = None