from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "TurfOps"
    database_url: str = "sqlite:///./turfops.db"
    secret_key: str = "change-me-in-production"
    admin_username: str = "cory"
    admin_password: str = "changeme"
    nominatim_user_agent: str = "turfops/1.0"

    # Service area center (Lakeway, TX)
    service_area_lat: float = 30.3913
    service_area_lon: float = -97.9461

    # Analytics & ads (set in Railway env vars when ready)
    ga_measurement_id: str = ""       # e.g. G-XXXXXXXXXX
    google_ads_id: str = ""           # e.g. AW-XXXXXXXXX
    google_ads_conversion: str = ""   # e.g. AW-XXXXXXXXX/XXXXXXXX
    fb_pixel_id: str = ""             # e.g. 1234567890

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
