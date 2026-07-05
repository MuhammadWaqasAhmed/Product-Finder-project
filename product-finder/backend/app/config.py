from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Product Finder"
    secret_key: str = "change-me-in-production-use-a-long-random-string"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "sqlite:///./product_finder.db"

    amazon_access_key: str = ""
    amazon_secret_key: str = ""
    amazon_partner_tag: str = ""
    amazon_marketplace: str = "US"

    ebay_app_id: str = ""
    ebay_cert_id: str = ""
    ebay_dev_id: str = ""

    tiktok_shop_app_key: str = ""
    tiktok_shop_app_secret: str = ""

    aliexpress_app_key: str = ""
    aliexpress_app_secret: str = ""

    alibaba_app_key: str = ""
    alibaba_app_secret: str = ""

    china_market_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
