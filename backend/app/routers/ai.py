"""AI advisor router."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.ai import StartupAdvisorProvider, get_advisor_provider

router = APIRouter(prefix="/ai", tags=["ai"])


class IdeaRef(BaseModel):
    idea_id: str | None = None
    title: str = Field(min_length=1, max_length=200)
    problem: str | None = None
    solution: str | None = None
    audience: str | None = None
    category: str | None = None


class CompetitorRef(IdeaRef):
    market: str | None = None


def _to_idea_dict(payload: BaseModel) -> dict[str, Any]:
    return {k: v for k, v in payload.model_dump().items() if v is not None}


@router.post("/validate", summary="Validate an idea")
async def validate_idea(
    payload: IdeaRef,
    provider: StartupAdvisorProvider = Depends(get_advisor_provider),
):
    return await provider.validate(_to_idea_dict(payload))


@router.post("/swot-suggestions", summary="Suggest SWOT entries")
async def swot_suggestions(
    payload: IdeaRef,
    provider: StartupAdvisorProvider = Depends(get_advisor_provider),
):
    return await provider.swot_suggestions(_to_idea_dict(payload))


@router.post("/risk-suggestions", summary="Suggest risks")
async def risk_suggestions(
    payload: IdeaRef,
    provider: StartupAdvisorProvider = Depends(get_advisor_provider),
):
    return await provider.risk_suggestions(_to_idea_dict(payload))


@router.post("/competitors", summary="Suggest competitors to analyse")
async def competitor_recommendations(
    payload: CompetitorRef,
    provider: StartupAdvisorProvider = Depends(get_advisor_provider),
):
    return await provider.competitor_recommendations(
        _to_idea_dict(payload), payload.market
    )


@router.post("/growth-roadmap", summary="Suggest a growth roadmap")
async def growth_roadmap(
    payload: IdeaRef,
    provider: StartupAdvisorProvider = Depends(get_advisor_provider),
):
    return await provider.growth_roadmap(_to_idea_dict(payload))