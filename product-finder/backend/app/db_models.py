from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    search_history: Mapped[list["SearchHistory"]] = relationship(back_populates="user")
    integrations: Mapped[list["InfluencerIntegration"]] = relationship(back_populates="user")
    workflows: Mapped[list["AIWorkflow"]] = relationship(back_populates="user")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    query: Mapped[str] = mapped_column(String(255), default="")
    providers: Mapped[str] = mapped_column(String(255), default="all")
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    filters_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User | None] = relationship(back_populates="search_history")


class CachedProduct(Base):
    __tablename__ = "cached_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(255), index=True)
    provider: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(120), default="General")
    brand: Mapped[str] = mapped_column(String(120), default="Unknown")
    price: Mapped[float] = mapped_column(Float, default=0)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    rating: Mapped[float] = mapped_column(Float, default=0)
    reviews: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str] = mapped_column(Text, default="")
    tags_json: Mapped[str] = mapped_column(Text, default="[]")
    image_url: Mapped[str] = mapped_column(Text, default="")
    product_url: Mapped[str] = mapped_column(Text, default="")
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    raw_json: Mapped[str] = mapped_column(Text, default="{}")
    cached_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class InfluencerProfile(Base):
    __tablename__ = "influencer_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    display_name: Mapped[str] = mapped_column(String(255))
    niche: Mapped[str] = mapped_column(String(120), default="")
    audience_size: Mapped[int] = mapped_column(Integer, default=0)
    bio: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class InfluencerIntegration(Base):
    __tablename__ = "influencer_integrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    platform: Mapped[str] = mapped_column(String(80))
    account_handle: Mapped[str] = mapped_column(String(255))
    account_id: Mapped[str] = mapped_column(String(255), default="")
    access_token: Mapped[str] = mapped_column(Text, default="")
    refresh_token: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="connected")
    ai_workflow_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    workflow_preferences_json: Mapped[str] = mapped_column(Text, default="{}")
    connected_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="integrations")


class AIWorkflow(Base):
    __tablename__ = "ai_workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))
    trigger: Mapped[str] = mapped_column(String(120))
    actions_json: Mapped[str] = mapped_column(Text, default="[]")
    schedule: Mapped[str] = mapped_column(String(80), default="daily")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="workflows")
