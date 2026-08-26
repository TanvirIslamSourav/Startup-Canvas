"""AI advisor package — swappable provider interface + mock implementation.

The router layer depends only on the ``StartupAdvisorProvider`` protocol.
Adding a new provider (OpenAI, Gemini, …) is purely additive: implement the
protocol, register the class, flip the env var.
"""
from app.ai.provider import (
    AdviceItem,
    AdviceResult,
    StartupAdvisorProvider,
    get_advisor_provider,
)

__all__ = [
    "AdviceItem",
    "AdviceResult",
    "StartupAdvisorProvider",
    "get_advisor_provider",
]