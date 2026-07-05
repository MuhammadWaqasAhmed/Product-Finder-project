from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..db_models import User
from ..schemas import (
    AIWorkflowCreate,
    AIWorkflowPublic,
    InfluencerDashboard,
    InfluencerIntegrationCreate,
    InfluencerIntegrationPublic,
    InfluencerProfileCreate,
)
from ..services.influencer_service import (
    connect_integration,
    create_workflow,
    get_influencer_dashboard,
    upsert_profile,
)

router = APIRouter(prefix="/api/influencer", tags=["influencer"])


@router.get("/dashboard", response_model=InfluencerDashboard)
def influencer_dashboard(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> InfluencerDashboard:
    return get_influencer_dashboard(db, user)


@router.post("/profile", response_model=InfluencerProfileCreate)
def save_profile(
    payload: InfluencerProfileCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> InfluencerProfileCreate:
    return upsert_profile(db, user, payload)


@router.post("/integrations", response_model=InfluencerIntegrationPublic)
def save_integration(
    payload: InfluencerIntegrationCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> InfluencerIntegrationPublic:
    return connect_integration(db, user, payload)


@router.post("/workflows", response_model=AIWorkflowPublic)
def save_workflow(
    payload: AIWorkflowCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> AIWorkflowPublic:
    return create_workflow(db, user, payload)
