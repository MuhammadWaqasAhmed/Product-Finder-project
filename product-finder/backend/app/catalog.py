from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .schemas import MarketplaceProvider, Product

DATA_PATH = Path(__file__).resolve().parent / "data" / "products.json"


@lru_cache
def load_local_products() -> list[Product]:
    with DATA_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    products: list[Product] = []
    for item in payload:
        products.append(
            Product(
                id=f"local:{item['id']}",
                name=item["name"],
                category=item["category"],
                brand=item["brand"],
                price=item["price"],
                rating=item["rating"],
                reviews=item["reviews"],
                description=item["description"],
                tags=item["tags"],
                in_stock=item.get("in_stock", True),
                provider=MarketplaceProvider.LOCAL,
                image_url=f"https://picsum.photos/seed/local-{item['id']}/400/400",
                product_url=f"https://example.com/local/{item['id']}",
            )
        )
    return products
