from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # База данных
    DATABASE_URL: str = "postgresql://postgres:postgres123@localhost:5432/subscriptions_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 дней (7 * 24 * 60 = 10080 минут)
    
    # Настройки приложения
    APP_NAME: str = "Subscription Manager"
    DEBUG: bool = True
    
    # Настройки уведомлений
    NOTIFICATION_DAYS_BEFORE: int = 7
    
    class Config:
        env_file = ".env"

settings = Settings() 