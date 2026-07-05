from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from ..catalog import load_local_products
from ..db_models import CachedProduct, SearchHistory, User
from ..providers import get_all_providers, provider_label
from ..schemas import MarketplaceProvider, Product, SearchResponse, SearchResult
from ..search import search_products


def _cache_product(db: Session, product: Product) -> None:
    existing = (
        db.query(CachedProduct)
        .filter(
            CachedProduct.external_id == product.id.split(":", 1)[-1],
            CachedProduct.provider == product.provider.value,
        )
        .first()
    )
    payload = product.model_dump()
    if existing:
        existing.name = product.name
        existing.category = product.category
        existing.brand = product.brand
        existing.price = product.price
        existing.currency = product.currency
        existing.rating = product.rating
        existing.reviews = product.reviews
        existing.description = product.description
        existing.tags_json = json.dumps(product.tags)
        existing.image_url = product.image_url
        existing.product_url = product.product_url
        existing.in_stock = product.in_stock
        existing.raw_json = json.dumps(payload)
        existing.cached_at = datetime.now(UTC)
        return

    db.add(
        CachedProduct(
            external_id=product.id.split(":", 1)[-1],
            provider=product.provider.value,
            name=product.name,
            category=product.category,
            brand=product.brand,
            price=product.price,
            currency=product.currency,
            rating=product.rating,
            reviews=product.reviews,
            description=product.description,
            tags_json=json.dumps(product.tags),
            image_url=product.image_url,
            product_url=product.product_url,
            in_stock=product.in_stock,
            raw_json=json.dumps(payload),
        )
    )


async def _fetch_provider_products(query: str, limit: int) -> tuple[list[Product], list[str], list[str]]:
    providers = get_all_providers()
    tasks = [provider.search(query, limit=limit) for provider in providers]
    results = await asyncio.gather(*tasks)

    products: list[Product] = []
    live: list[str] = []
    demo: list[str] = []

    for result in results:
        products.extend(result.products)
        label = provider_label(result.provider)
        if result.live:
            live.append(label)
        else:
            demo.append(label)
    return products, live, demo


async def unified_search(
    db: Session,
    *,
    query: str = "",
    category: str | None = None,
    brand: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
    providers: list[str] | None = None,
    limit: int = 10,
    user: User | None = None,
) -> SearchResponse:
    local_products = load_local_products()
    marketplace_products, live_providers, demo_providers = await _fetch_provider_products(query, limit)
    all_products = local_products + marketplace_products

    if providers:
        allowed = {item.lower() for item in providers}
        all_products = [product for product in all_products if product.provider.value in allowed]

    results = search_products(
        query,
        all_products,
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only,
        limit=limit,
    )

    for product in results:
        _cache_product(db, product)
    db.commit()

    categories = sorted({product.category for product in all_products})
    brands = sorted({product.brand for product in all_products})
    provider_names = sorted({provider_label(product.provider) for product in all_products})
    prices = [product.price for product in all_products] or [0]
    avg_rating = round(sum(product.rating for product in all_products) / len(all_products), 2)

    db.add(
        SearchHistory(
            user_id=user.id if user else None,
            query=query,
            providers=",".join(providers or ["all"]),
            result_count=len(results),
            filters_json=json.dumps(
                {
                    "category": category,
                    "brand": brand,
                    "min_price": min_price,
                    "max_price": max_price,
                    "in_stock_only": in_stock_only,
                }
            ),
        )
    )
    db.commit()

    return SearchResponse(
        query=query,
        total_matches=len(results),
        results=results,
        categories=categories,
        brands=brands,
        providers=provider_names,
        price_range={"min": min(prices), "max": max(prices)},
        avg_rating=avg_rating,
        live_providers=live_providers,
        demo_providers=demo_providers,
    )
