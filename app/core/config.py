"""
Application Configuration
Load settings from environment variables
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env file"""

    # Database
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application
    APP_NAME: str = "Robis ERP API"
    DEBUG: bool = False

    # Google Gemini AI (NEW)
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_MAX_TOKENS: int = 1000
    GEMINI_TEMPERATURE: float = 0.7

    # Public QR/Kiosk Service Token (NEW)
    ATTEND_PUBLIC_TOKEN: Optional[str] = None

    # Public Employees endpoint options (NEW)
    PUBLIC_EMPLOYEES_OPEN: bool = False  # Cho phép GET /api/v1/public/employees không cần token
    PUBLIC_EMPLOYEES_MIN_SEARCH_LEN: int = 2  # Bắt buộc search tối thiểu N ký tự khi mở public
    PUBLIC_EMPLOYEES_MAX_PAGE_SIZE: int = 20  # Giới hạn page_size khi mở public

    # Public Attendance actions (check-in/out/leave) open toggle (NEW)
    PUBLIC_ATTEND_ACTIONS_OPEN: bool = False  # Cho phép check-in/out/leave không cần token (bypass)
    PUBLIC_KIOSK_IP_WHITELIST: Optional[str] = None  # CSV IP whitelist, ví dụ: "192.168.1.10,192.168.1.11"
    PUBLIC_KIOSK_DEVICE_SECRET: Optional[str] = None  # Secret cho kiosk gửi trong header X-Kiosk-Secret

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields in .env
    )

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# Create settings instance
settings = Settings()
