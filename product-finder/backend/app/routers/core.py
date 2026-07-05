from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..auth import get_current_user_optional
from ..database import get_db
from ..db_models import User
from ..schemas import AnalyticsDashboard, SearchResponse
from ..services.dashboard_service import build_analytics_dashboard
from ..services.search_service import unified_search

router = APIRouter(prefix="/api", tags=["core"])


@router.get("/dashboard", response_model=AnalyticsDashboard)
def dashboard(db: Annotated[Session, Depends(get_db)]) -> AnalyticsDashboard:
    return build_analytics_dashboard(db)


@router.get("/search", response_model=SearchResponse)
async def search(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_current_user_optional)],
    q: str = Query(default="", max_length=120),
    category: str | None = None,
    brand: str | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    in_stock_only: bool = False,
    providers: str | None = Query(default=None, description="Comma-separated provider keys"),
    limit: int = Query(default=10, ge=1, le=50),
) -> SearchResponse:
    provider_list = [item.strip() for item in providers.split(",")] if providers else None
    return await unified_search(
        db,
        query=q,
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only,
        providers=provider_list,
        limit=limit,
        user=user,
    )
