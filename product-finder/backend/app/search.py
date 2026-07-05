from __future__ import annotations

import re
from difflib import SequenceMatcher

from .schemas import Product, SearchResult


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


def _token_overlap(query_tokens: set[str], text: str) -> float:
    text_tokens = set(_normalize(text).split())
    if not query_tokens:
        return 0.0
    overlap = query_tokens & text_tokens
    return len(overlap) / len(query_tokens)


def _match_reasons(query: str, product: Product, query_tokens: set[str]) -> list[str]:
    reasons: list[str] = []
    q = _normalize(query)

    if q and q in _normalize(product.name):
        reasons.append("Name match")
    if q and q in _normalize(product.brand):
        reasons.append("Brand match")
    if q and q in _normalize(product.category):
        reasons.append("Category match")

    tag_hits = [tag for tag in product.tags if tag in query_tokens or q in _normalize(tag)]
    if tag_hits:
        reasons.append(f"Tag match: {', '.join(tag_hits[:3])}")

    if q and q in _normalize(product.description):
        reasons.append("Description match")

    if not reasons and query_tokens:
        reasons.append("Partial keyword match")

    return reasons


def score_product(query: str, product: Product) -> tuple[float, list[str]]:
    if not query.strip():
        return 0.0, []

    q = _normalize(query)
    query_tokens = set(q.split())

    name_sim = _similarity(q, product.name)
    brand_sim = _similarity(q, product.brand)
    category_sim = _similarity(q, product.category)
    desc_sim = _similarity(q, product.description[:120])

    name_overlap = _token_overlap(query_tokens, product.name)
    tag_overlap = _token_overlap(query_tokens, " ".join(product.tags))
    desc_overlap = _token_overlap(query_tokens, product.description)

    exact_name = 1.0 if q in _normalize(product.name) else 0.0
    exact_brand = 1.0 if q in _normalize(product.brand) else 0.0
    exact_category = 1.0 if q in _normalize(product.category) else 0.0

    raw_score = (
        exact_name * 35
        + exact_brand * 20
        + exact_category * 15
        + name_sim * 20
        + name_overlap * 15
        + brand_sim * 10
        + tag_overlap * 12
        + category_sim * 8
        + desc_overlap * 6
        + desc_sim * 4
    )

    if product.in_stock:
        raw_score += 2

    raw_score += min(product.rating, 5) * 0.5

    score = min(100.0, round(raw_score, 2))
    reasons = _match_reasons(query, product, query_tokens)

    return score, reasons


def search_products(
    query: str,
    products: list[Product],
    *,
    category: str | None = None,
    brand: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
    limit: int = 10,
) -> list[SearchResult]:
    filtered: list[Product] = []

    for product in products:
        if category and _normalize(product.category) != _normalize(category):
            continue
        if brand and _normalize(product.brand) != _normalize(brand):
            continue
        if min_price is not None and product.price < min_price:
            continue
        if max_price is not None and product.price > max_price:
            continue
        if in_stock_only and not product.in_stock:
            continue
        filtered.append(product)

    scored: list[SearchResult] = []
    for product in filtered:
        score, reasons = score_product(query, product)
        if query.strip() and score <= 0:
            continue
        scored.append(
            SearchResult(
                **product.model_dump(),
                score=score if query.strip() else round(product.rating * 20, 2),
                match_reasons=reasons if query.strip() else ["Browse mode"],
            )
        )

    scored.sort(key=lambda item: (-item.score, -item.rating, -item.reviews, item.price))
    return scored[:limit]
