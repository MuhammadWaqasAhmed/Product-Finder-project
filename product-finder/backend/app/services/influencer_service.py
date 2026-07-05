from __future__ import annotations

import json

from sqlalchemy.orm import Session

from ..auth import get_password_hash
from ..db_models import AIWorkflow, InfluencerIntegration, InfluencerProfile, User
from ..schemas import (
    AIWorkflowCreate,
    AIWorkflowPublic,
    InfluencerDashboard,
    InfluencerIntegrationCreate,
    InfluencerIntegrationPublic,
    InfluencerProfileCreate,
)


AVAILABLE_PLATFORMS = [
    "TikTok",
    "Instagram",
    "YouTube",
    "Amazon Associates",
    "eBay Partner Network",
    "AliExpress Portals",
    "Alibaba Seller",
    "Shopify",
    "Pinterest",
]

AI_CAPABILITIES = [
    "Automated product research from trending niches",
    "AI-generated affiliate content and captions",
    "Price drop alerts across connected marketplaces",
    "Competitor product monitoring",
    "Smart posting schedule recommendations",
    "Campaign performance summaries",
]


def ensure_demo_user(db: Session) -> User:
    user = db.query(User).filter(User.username == "demo").first()
    if user:
        if user.email != "demo@example.com":
            user.email = "demo@example.com"
            db.commit()
        return user
    user = User(
        email="demo@example.com",
        username="demo",
        full_name="Demo Influencer",
        hashed_password=get_password_hash("demo1234"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_influencer_dashboard(db: Session, user: User) -> InfluencerDashboard:
    profile = db.query(InfluencerProfile).filter(InfluencerProfile.user_id == user.id).first()
    integrations = db.query(InfluencerIntegration).filter(InfluencerIntegration.user_id == user.id).all()
    workflows = db.query(AIWorkflow).filter(AIWorkflow.user_id == user.id).all()

    return InfluencerDashboard(
        profile=(
            InfluencerProfileCreate(
                display_name=profile.display_name,
                niche=profile.niche,
                audience_size=profile.audience_size,
                bio=profile.bio,
            )
            if profile
            else None
        ),
        integrations=[
            InfluencerIntegrationPublic(
                id=item.id,
                platform=item.platform,
                account_handle=item.account_handle,
                status=item.status,
                ai_workflow_enabled=item.ai_workflow_enabled,
                workflow_preferences=json.loads(item.workflow_preferences_json or "{}"),
                connected_at=item.connected_at,
            )
            for item in integrations
        ],
        workflows=[
            AIWorkflowPublic(
                id=item.id,
                name=item.name,
                trigger=item.trigger,
                actions=json.loads(item.actions_json or "[]"),
                schedule=item.schedule,
                enabled=item.enabled,
                last_run_at=item.last_run_at,
            )
            for item in workflows
        ],
        available_platforms=AVAILABLE_PLATFORMS,
        ai_capabilities=AI_CAPABILITIES,
    )


def upsert_profile(db: Session, user: User, payload: InfluencerProfileCreate) -> InfluencerProfileCreate:
    profile = db.query(InfluencerProfile).filter(InfluencerProfile.user_id == user.id).first()
    if not profile:
        profile = InfluencerProfile(user_id=user.id)
        db.add(profile)
    profile.display_name = payload.display_name
    profile.niche = payload.niche
    profile.audience_size = payload.audience_size
    profile.bio = payload.bio
    db.commit()
    return payload


def connect_integration(
    db: Session,
    user: User,
    payload: InfluencerIntegrationCreate,
) -> InfluencerIntegrationPublic:
    integration = InfluencerIntegration(
        user_id=user.id,
        platform=payload.platform,
        account_handle=payload.account_handle,
        account_id=payload.account_id,
        access_token=payload.access_token,
        refresh_token=payload.refresh_token,
        status="connected" if payload.access_token or payload.account_handle else "pending",
        ai_workflow_enabled=payload.ai_workflow_enabled,
        workflow_preferences_json=json.dumps(payload.workflow_preferences),
    )
    db.add(integration)
    db.commit()
    db.refresh(integration)

    return InfluencerIntegrationPublic(
        id=integration.id,
        platform=integration.platform,
        account_handle=integration.account_handle,
        status=integration.status,
        ai_workflow_enabled=integration.ai_workflow_enabled,
        workflow_preferences=json.loads(integration.workflow_preferences_json or "{}"),
        connected_at=integration.connected_at,
    )


def create_workflow(db: Session, user: User, payload: AIWorkflowCreate) -> AIWorkflowPublic:
    workflow = AIWorkflow(
        user_id=user.id,
        name=payload.name,
        trigger=payload.trigger,
        actions_json=json.dumps(payload.actions),
        schedule=payload.schedule,
        enabled=payload.enabled,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return AIWorkflowPublic(
        id=workflow.id,
        name=workflow.name,
        trigger=workflow.trigger,
        actions=json.loads(workflow.actions_json or "[]"),
        schedule=workflow.schedule,
        enabled=workflow.enabled,
        last_run_at=workflow.last_run_at,
    )
