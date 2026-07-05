from __future__ import annotations

import json
from dataclasses import dataclass

from ..schemas import MarketplaceProvider, Product


@dataclass
class ProviderResult:
    provider: MarketplaceProvider
    products: list[Product]
    live: bool


class BaseProvider:
    provider: MarketplaceProvider
    label: str = ""

    async def search(self, query: str, limit: int = 10) -> ProviderResult:
        raise NotImplementedError

    def is_configured(self) -> bool:
        return False


def _demo_product(
    provider: MarketplaceProvider,
    external_id: str,
    name: str,
    category: str,
    brand: str,
    price: float,
    rating: float,
    reviews: int,
    description: str,
    tags: list[str],
    *,
    currency: str = "USD",
    in_stock: bool = True,
) -> Product:
    slug = external_id.replace(" ", "-").lower()
    return Product(
        id=f"{provider.value}:{external_id}",
        name=name,
        category=category,
        brand=brand,
        price=price,
        currency=currency,
        rating=rating,
        reviews=reviews,
        description=description,
        tags=tags,
        in_stock=in_stock,
        provider=provider,
        image_url=f"https://picsum.photos/seed/{slug}/400/400",
        product_url=f"https://example.com/{provider.value}/{slug}",
    )


DEMO_CATALOG: dict[MarketplaceProvider, list[dict]] = {
    MarketplaceProvider.AMAZON: [
        {
            "id": "amz-001",
            "name": "Echo Dot (5th Gen) Smart Speaker",
            "category": "Electronics",
            "brand": "Amazon",
            "price": 49.99,
            "rating": 4.7,
            "reviews": 98000,
            "description": "Compact smart speaker with Alexa voice control and rich sound.",
            "tags": ["smart-home", "speaker", "alexa"],
        },
        {
            "id": "amz-002",
            "name": "Fire TV Stick 4K Max Streaming Device",
            "category": "Electronics",
            "brand": "Amazon",
            "price": 59.99,
            "rating": 4.6,
            "reviews": 54000,
            "description": "Stream 4K content with Wi-Fi 6 support and Alexa voice remote.",
            "tags": ["streaming", "tv", "entertainment"],
        },
    ],
    MarketplaceProvider.EBAY: [
        {
            "id": "ebay-001",
            "name": "Vintage Levis 501 Jeans",
            "category": "Clothing",
            "brand": "Levi's",
            "price": 68.0,
            "rating": 4.4,
            "reviews": 210,
            "description": "Pre-owned classic denim with authentic vintage wash.",
            "tags": ["vintage", "denim", "fashion"],
        },
        {
            "id": "ebay-002",
            "name": "Nintendo Switch OLED Console Bundle",
            "category": "Gaming",
            "brand": "Nintendo",
            "price": 329.99,
            "rating": 4.8,
            "reviews": 890,
            "description": "Popular hybrid console bundle with accessories from trusted seller.",
            "tags": ["gaming", "console", "bundle"],
        },
    ],
    MarketplaceProvider.TIKTOK_SHOP: [
        {
            "id": "tt-001",
            "name": "Viral LED Sunset Lamp",
            "category": "Home Decor",
            "brand": "GlowHaus",
            "price": 24.99,
            "rating": 4.5,
            "reviews": 18200,
            "description": "Trending ambient lamp featured in lifestyle creator videos.",
            "tags": ["viral", "decor", "tiktok"],
        },
        {
            "id": "tt-002",
            "name": "Portable Mini Blender Cup",
            "category": "Kitchen",
            "brand": "BlendGo",
            "price": 19.99,
            "rating": 4.3,
            "reviews": 9600,
            "description": "USB rechargeable blender popular with fitness influencers.",
            "tags": ["kitchen", "portable", "fitness"],
        },
    ],
    MarketplaceProvider.ALIEXPRESS: [
        {
            "id": "ae-001",
            "name": "Wireless Earbuds Pro Clone",
            "category": "Electronics",
            "brand": "SoundLite",
            "price": 18.5,
            "rating": 4.2,
            "reviews": 42000,
            "description": "Budget-friendly wireless earbuds with ANC and charging case.",
            "tags": ["earbuds", "budget", "wireless"],
        },
        {
            "id": "ae-002",
            "name": "Smart Watch Fitness Tracker",
            "category": "Wearables",
            "brand": "FitPulse",
            "price": 22.9,
            "rating": 4.1,
            "reviews": 31000,
            "description": "Affordable fitness watch with heart-rate and sleep tracking.",
            "tags": ["watch", "fitness", "affordable"],
        },
    ],
    MarketplaceProvider.ALIBABA: [
        {
            "id": "ali-001",
            "name": "Wholesale Cotton T-Shirts (100 pcs)",
            "category": "Apparel",
            "brand": "TextileCo",
            "price": 280.0,
            "rating": 4.6,
            "reviews": 120,
            "description": "Bulk blank tees for private label brands and resellers.",
            "tags": ["wholesale", "apparel", "b2b"],
        },
        {
            "id": "ali-002",
            "name": "Custom Logo Packaging Boxes MOQ 500",
            "category": "Packaging",
            "brand": "PackMaster",
            "price": 450.0,
            "rating": 4.7,
            "reviews": 85,
            "description": "Customizable shipping boxes for e-commerce brands.",
            "tags": ["packaging", "b2b", "custom"],
        },
    ],
    MarketplaceProvider.CHINA_MARKET: [
        {
            "id": "cn-001",
            "name": "1688 Factory Direct Phone Case Lot",
            "category": "Accessories",
            "brand": "Shenzhen OEM",
            "price": 95.0,
            "currency": "CNY",
            "rating": 4.5,
            "reviews": 640,
            "description": "Mixed-model phone case lot sourced from Guangdong manufacturers.",
            "tags": ["1688", "factory", "mobile"],
        },
        {
            "id": "cn-002",
            "name": "Cross-border Hot Seller Desk Organizer",
            "category": "Office",
            "brand": "Yiwu Trade",
            "price": 36.0,
            "currency": "CNY",
            "rating": 4.4,
            "reviews": 2100,
            "description": "Fast-moving desk organizer popular on domestic marketplaces.",
            "tags": ["yiwu", "office", "cross-border"],
        },
    ],
}


def _matches_query(query: str, item: dict) -> bool:
    if not query.strip():
        return True
    haystack = " ".join(
        [
            item["name"],
            item["category"],
            item["brand"],
            item["description"],
            " ".join(item["tags"]),
        ]
    ).lower()
    tokens = query.lower().split()
    return all(token in haystack for token in tokens)


class DemoMarketplaceProvider(BaseProvider):
    def __init__(self, provider: MarketplaceProvider, label: str) -> None:
        self.provider = provider
        self.label = label

    async def search(self, query: str, limit: int = 10) -> ProviderResult:
        catalog = DEMO_CATALOG.get(self.provider, [])
        products = [
            _demo_product(self.provider, **item)
            for item in catalog
            if _matches_query(query, item)
        ][:limit]
        return ProviderResult(provider=self.provider, products=products, live=False)


class AmazonProvider(DemoMarketplaceProvider):
    provider = MarketplaceProvider.AMAZON

    def __init__(self) -> None:
        super().__init__(MarketplaceProvider.AMAZON, "Amazon")

    def is_configured(self) -> bool:
        from ..config import get_settings

        settings = get_settings()
        return bool(settings.amazon_access_key and settings.amazon_secret_key and settings.amazon_partner_tag)


class EbayProvider(DemoMarketplaceProvider):
    provider = MarketplaceProvider.EBAY

    def __init__(self) -> None:
        super().__init__(MarketplaceProvider.EBAY, "eBay")

    def is_configured(self) -> bool:
        from ..config import get_settings

        settings = get_settings()
        return bool(settings.ebay_app_id)


class TikTokShopProvider(DemoMarketplaceProvider):
    provider = MarketplaceProvider.TIKTOK_SHOP

    def __init__(self) -> None:
        super().__init__(MarketplaceProvider.TIKTOK_SHOP, "TikTok Shop")

    def is_configured(self) -> bool:
        from ..config import get_settings

        settings = get_settings()
        return bool(settings.tiktok_shop_app_key and settings.tiktok_shop_app_secret)


class AliExpressProvider(DemoMarketplaceProvider):
    provider = MarketplaceProvider.ALIEXPRESS

    def __init__(self) -> None:
        super().__init__(MarketplaceProvider.ALIEXPRESS, "AliExpress")

    def is_configured(self) -> bool:
        from ..config import get_settings

        settings = get_settings()
        return bool(settings.aliexpress_app_key and settings.aliexpress_app_secret)


class AlibabaProvider(DemoMarketplaceProvider):
    provider = MarketplaceProvider.ALIBABA

    def __init__(self) -> None:
        super().__init__(MarketplaceProvider.ALIBABA, "Alibaba")

    def is_configured(self) -> bool:
        from ..config import get_settings

        settings = get_settings()
        return bool(settings.alibaba_app_key and settings.alibaba_app_secret)


class ChinaMarketProvider(DemoMarketplaceProvider):
    provider = MarketplaceProvider.CHINA_MARKET

    def __init__(self) -> None:
        super().__init__(MarketplaceProvider.CHINA_MARKET, "China Market")

    def is_configured(self) -> bool:
        from ..config import get_settings

        settings = get_settings()
        return bool(settings.china_market_api_key)


def get_all_providers() -> list[BaseProvider]:
    return [
        AmazonProvider(),
        EbayProvider(),
        TikTokShopProvider(),
        AliExpressProvider(),
        AlibabaProvider(),
        ChinaMarketProvider(),
    ]


def provider_label(provider: MarketplaceProvider | str) -> str:
    mapping = {
        MarketplaceProvider.LOCAL: "Local Catalog",
        MarketplaceProvider.AMAZON: "Amazon",
        MarketplaceProvider.EBAY: "eBay",
        MarketplaceProvider.TIKTOK_SHOP: "TikTok Shop",
        MarketplaceProvider.ALIEXPRESS: "AliExpress",
        MarketplaceProvider.ALIBABA: "Alibaba",
        MarketplaceProvider.CHINA_MARKET: "China Market",
    }
    if isinstance(provider, str):
        try:
            provider = MarketplaceProvider(provider)
        except ValueError:
            return provider
    return mapping.get(provider, provider.value)
