import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    APP_NAME: str = "WhatsApp Cloud API Gateway"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Meta WhatsApp Business Cloud API Credentials
    WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "")
    PHONE_NUMBER_ID: str = os.getenv("PHONE_NUMBER_ID", "")
    VERIFY_TOKEN: str = os.getenv("VERIFY_TOKEN", "default_secure_verification_token")
    APP_SECRET: str = os.getenv("APP_SECRET", "")
    API_VERSION: str = os.getenv("API_VERSION", "v21.0")

    @property
    def messages_endpoint(self) -> str:
        return f"https://graph.facebook.com/{self.API_VERSION}/{self.PHONE_NUMBER_ID}/messages"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
