"""MockStartupAdvisorProvider — reads canned responses from local JSON."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.ai.provider import AdviceItem, AdviceResult, _now_iso, empty_result


class MockStartupAdvisorProvider:
    """Local, deterministic advisor.

    Looks up suggestions by matching keywords found in the idea's
    ``title``/``problem``/``solution`` against a JSON map. Falls back to
    ``_default`` if no keyword matches.
    """

    name = "mock"
    model = "local-json-v1"

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)
        self._cache: dict[str, list[AdviceItem]] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load(self, capability: str) -> list[AdviceItem]:
        if capability in self._cache:
            return self._cache[capability]
        path = self.data_dir / f"{capability}.json"
        if not path.exists():
            self._cache[capability] = []
            return []
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            self._cache[capability] = []
            return []
        # Normalize to flat list
        items: list[AdviceItem] = []
        for _key, value in raw.items():
            if isinstance(value, list):
                for entry in value:
                    items.append(
                        AdviceItem(
                            title=str(entry.get("title", "")),
                            detail=str(entry.get("detail", "")),
                            confidence=float(entry.get("confidence", 0.5)),
                        )
                    )
        self._cache[capability] = items
        return items

    @staticmethod
    def _haystack(idea: dict[str, Any]) -> str:
        return " ".join(
            str(idea.get(k, "") or "") for k in ("title", "problem", "solution", "audience")
        ).lower()

    def _match(self, items: list[AdviceItem], idea: dict[str, Any]) -> list[AdviceItem]:
        haystack = self._haystack(idea)
        hits: list[AdviceItem] = []
        for item in items:
            title_words = [w.lower() for w in item["title"].split() if len(w) > 3]
            if any(word in haystack for word in title_words):
                hits.append(item)
        return hits or items[:3]  # fall back to first 3 generic items

    def _result(self, items: list[AdviceItem]) -> AdviceResult:
        return AdviceResult(
            provider=self.name,
            model=self.model,
            content=items,
            generated_at=_now_iso(),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def validate(self, idea: dict[str, Any]) -> AdviceResult:
        items = self._match(self._load("validate"), idea)
        return self._result(items)

    async def swot_suggestions(self, idea: dict[str, Any]) -> AdviceResult:
        items = self._match(self._load("swot"), idea)
        return self._result(items)

    async def risk_suggestions(self, idea: dict[str, Any]) -> AdviceResult:
        items = self._match(self._load("risks"), idea)
        return self._result(items)

    async def competitor_recommendations(
        self, idea: dict[str, Any], market: str | None
    ) -> AdviceResult:
        items = self._match(self._load("competitors"), idea)
        if market:
            items = [
                AdviceItem(
                    title=f"{market} market scan",
                    detail=f"Consider how {market} incumbents price, position, and retain customers.",
                    confidence=0.6,
                ),
                *items,
            ]
        return self._result(items)

    async def growth_roadmap(self, idea: dict[str, Any]) -> AdviceResult:
        items = self._match(self._load("growth"), idea)
        if not items:
            return empty_result(self.name, self.model)
        return self._result(items)