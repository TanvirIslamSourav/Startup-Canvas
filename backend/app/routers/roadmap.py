"""HTTP routes for roadmap and nested stages."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.roadmap import RoadmapCreate, RoadmapRead, RoadmapUpdate
from app.schemas.roadmap_stage import (
    RoadmapStageCreate,
    RoadmapStageListResponse,
    RoadmapStageRead,
    RoadmapStageUpdate,
)
from app.services import roadmap as roadmap_service

router = APIRouter(prefix="/ideas/{idea_id}/roadmap", tags=["roadmap"])


# --- 1:1 roadmap ----------------------------------------------------------

@router.get("", response_model=RoadmapRead | None, summary="Get the roadmap")
def get_roadmap(
    idea_id: UUID, db: Session = Depends(get_db)
) -> RoadmapRead | None:
    row = roadmap_service.get(db, idea_id)
    return RoadmapRead.model_validate(row) if row else None


@router.put(
    "", response_model=RoadmapRead, summary="Create-or-replace the roadmap"
)
def put_roadmap(
    idea_id: UUID,
    payload: RoadmapCreate,
    db: Session = Depends(get_db),
) -> RoadmapRead:
    row = roadmap_service.upsert(db, idea_id, payload)
    return RoadmapRead.model_validate(row)


@router.patch("", response_model=RoadmapRead, summary="Update the roadmap")
def patch_roadmap(
    idea_id: UUID,
    payload: RoadmapUpdate,
    db: Session = Depends(get_db),
) -> RoadmapRead:
    row = roadmap_service.update(db, idea_id, payload)
    return RoadmapRead.model_validate(row)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete the roadmap (and its stages)",
)
def delete_roadmap(
    idea_id: UUID, db: Session = Depends(get_db)
) -> Response:
    roadmap_service.delete(db, idea_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- 1:N stages under roadmap --------------------------------------------

@router.get(
    "/stages",
    response_model=RoadmapStageListResponse,
    summary="List roadmap stages",
)
def list_stages(
    idea_id: UUID,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> RoadmapStageListResponse:
    items, total = roadmap_service.list_stages(
        db, idea_id, limit=limit, offset=offset
    )
    return RoadmapStageListResponse(
        items=items, total=total, limit=limit, offset=offset
    )


@router.post(
    "/stages",
    response_model=RoadmapStageRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a roadmap stage",
)
def create_stage(
    idea_id: UUID,
    payload: RoadmapStageCreate,
    db: Session = Depends(get_db),
) -> RoadmapStageRead:
    row = roadmap_service.create_stage(db, idea_id, payload)
    return RoadmapStageRead.model_validate(row)


@router.get(
    "/stages/{stage_id}",
    response_model=RoadmapStageRead,
    summary="Get a roadmap stage",
)
def get_stage(
    idea_id: UUID, stage_id: UUID, db: Session = Depends(get_db)
) -> RoadmapStageRead:
    row = roadmap_service.get_stage(db, idea_id, stage_id)
    return RoadmapStageRead.model_validate(row)


@router.patch(
    "/stages/{stage_id}",
    response_model=RoadmapStageRead,
    summary="Update a roadmap stage",
)
def update_stage(
    idea_id: UUID,
    stage_id: UUID,
    payload: RoadmapStageUpdate,
    db: Session = Depends(get_db),
) -> RoadmapStageRead:
    row = roadmap_service.update_stage(db, idea_id, stage_id, payload)
    return RoadmapStageRead.model_validate(row)


@router.delete(
    "/stages/{stage_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a roadmap stage",
)
def delete_stage(
    idea_id: UUID, stage_id: UUID, db: Session = Depends(get_db)
) -> Response:
    roadmap_service.delete_stage(db, idea_id, stage_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)