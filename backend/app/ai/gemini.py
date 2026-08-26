"""Gemini provider stub."""
from __future__ import annotations

from typing import Any

from app.ai.provider import AdviceResult, StartupAdvisorProvider, empty_result
from app.core.exceptions import NotConfiguredError


class GeminiProvider(StartupAdvisorProvider):
    name = "gemini"

    async def validate(self, idea: dict[str, Any]) -> AdviceResult:
        raise NotConfiguredError(
            "GeminiProvider is not configured. Set GEMINI_API_KEY and implement this method."
        )

    async def swot_suggestions(self, idea: dict[str, Any]) -> AdviceResult:
        return empty_result(self.name, "unconfigured")

    async def risk_suggestions(self, idea: dict[str, Any]) -> AdviceResult:
        return empty_result(self.name, "unconfigured")

    async def competitor_recommendations(
        self, idea: dict[str, Any], market: str | None
    ) -> AdviceResult:
        return empty_result(self.name, "unconfigured")

    async def growth_roadmap(self, idea: dict[str, Any]) -> AdviceResult:
        return empty_result(self.name, "unconfigured")