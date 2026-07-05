from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class MarketplaceProvider(str, Enum):
    LOCAL = "local"
    AMAZON = "amazon"
    EBAY = "ebay"
    TIKTOK_SHOP = "tiktok_shop"
    ALIEXPRESS = "aliexpress"
    ALIBABA = "alibaba"
    CHINA_MARKET = "china_market"


class Product(BaseModel):
    id: str
    name: str
    category: str
    brand: str
    price: float = Field(ge=0)
    currency: str = "USD"
    rating: float = Field(ge=0, le=5)
    reviews: int = Field(ge=0)
    description: str
    tags: list[str]
    in_stock: bool = True
    provider: MarketplaceProvider = MarketplaceProvider.LOCAL
    image_url: str = ""
    product_url: str = ""


class SearchResult(Product):
    score: float = Field(ge=0, le=100)
    match_reasons: list[str]


class SearchResponse(BaseModel):
    query: str
    total_matches: int
    results: list[SearchResult]
    categories: list[str]
    brands: list[str]
    providers: list[str]
    price_range: dict[str, float]
    avg_rating: float
    live_providers: list[str]
    demo_providers: list[str]


class KpiCard(BaseModel):
    label: str
    value: str
    change: str
    trend: str


class ChartSeries(BaseModel):
    label: str
    data: list[float | int]


class ChartBlock(BaseModel):
    title: str
    labels: list[str]
    series: list[ChartSeries]


class LeaderboardEntry(BaseModel):
    rank: int
    name: str
    provider: str
    score: float
    value: str
    avatar_color: str


class ProviderStatus(BaseModel):
    provider: str
    label: str
    connected: bool
    mode: str
    product_count: int


class AnalyticsDashboard(BaseModel):
    kpis: list[KpiCard]
    search_volume: ChartBlock
    provider_mix: ChartBlock
    price_trends: ChartBlock
    category_breakdown: ChartBlock
    provider_engagement: ChartBlock
    top_products: list[LeaderboardEntry]
    provider_status: list[ProviderStatus]
    recent_searches: list[str]
    total_products: int
    total_searches: int


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    full_name: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    username: str
    full_name: str | None = None
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class InfluencerProfileCreate(BaseModel):
    display_name: str
    niche: str = ""
    audience_size: int = Field(default=0, ge=0)
    bio: str = ""


class InfluencerIntegrationCreate(BaseModel):
    platform: str
    account_handle: str
    account_id: str = ""
    access_token: str = ""
    refresh_token: str = ""
    ai_workflow_enabled: bool = True
    workflow_preferences: dict[str, bool | str] = Field(default_factory=dict)


class AIWorkflowCreate(BaseModel):
    name: str
    trigger: str
    actions: list[str]
    schedule: str = "daily"
    enabled: bool = True


class InfluencerIntegrationPublic(BaseModel):
    id: int
    platform: str
    account_handle: str
    status: str
    ai_workflow_enabled: bool
    workflow_preferences: dict[str, bool | str]
    connected_at: datetime


class AIWorkflowPublic(BaseModel):
    id: int
    name: str
    trigger: str
    actions: list[str]
    schedule: str
    enabled: bool
    last_run_at: datetime | None = None


class InfluencerDashboard(BaseModel):
    profile: InfluencerProfileCreate | None = None
    integrations: list[InfluencerIntegrationPublic]
    workflows: list[AIWorkflowPublic]
    available_platforms: list[str]
    ai_capabilities: list[str]
