import redis
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
from app.core.config import settings

# Подключение к Redis
try:
    redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=False)
    # Проверяем подключение
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception as e:
    print(f"Redis connection error: {e}")
    redis_client = None
    REDIS_AVAILABLE = False

class CacheManager:
    """Менеджер кэширования для приложения"""
    
    @staticmethod
    def get_key(prefix: str, user_id: int, suffix: str = "") -> str:
        """Генерирует ключ кэша для пользователя"""
        return f"{prefix}:user:{user_id}:{suffix}"
    
    @staticmethod
    def set_cache(key: str, data: Any, expire: int = 300) -> bool:
        """Сохраняет данные в кэш"""
        if not REDIS_AVAILABLE or not redis_client:
            return False
        try:
            serialized_data = pickle.dumps(data)
            return redis_client.setex(key, expire, serialized_data)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    @staticmethod
    def get_cache(key: str) -> Optional[Any]:
        """Получает данные из кэша"""
        if not REDIS_AVAILABLE or not redis_client:
            return None
        try:
            data = redis_client.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    @staticmethod
    def delete_cache(key: str) -> bool:
        """Удаляет данные из кэша"""
        if not REDIS_AVAILABLE or not redis_client:
            return False
        try:
            return bool(redis_client.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    @staticmethod
    def invalidate_user_cache(user_id: int, prefix: str = None) -> bool:
        """Инвалидирует весь кэш пользователя или по префиксу"""
        if not REDIS_AVAILABLE or not redis_client:
            return False
        try:
            if prefix:
                pattern = f"{prefix}:user:{user_id}:*"
            else:
                pattern = f"*:user:{user_id}:*"
            
            keys = redis_client.keys(pattern)
            if keys:
                return bool(redis_client.delete(*keys))
            return True
        except Exception as e:
            print(f"Cache invalidation error: {e}")
            return False
    
    @staticmethod
    def cache_decorator(prefix: str, expire: int = 300):
        """Декоратор для автоматического кэширования функций"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Извлекаем user_id из аргументов (обычно первый параметр после self)
                user_id = None
                for arg in args:
                    if hasattr(arg, 'id') and hasattr(arg, 'username'):
                        user_id = arg.id
                        break
                
                if not user_id:
                    return func(*args, **kwargs)
                
                cache_key = CacheManager.get_key(prefix, user_id)
                cached_data = CacheManager.get_cache(cache_key)
                
                if cached_data is not None:
                    return cached_data
                
                # Выполняем функцию и кэшируем результат
                result = func(*args, **kwargs)
                CacheManager.set_cache(cache_key, result, expire)
                return result
            
            return wrapper
        return decorator

# Утилиты для конкретных типов данных
class AnalyticsCache:
    """Кэширование аналитических данных"""
    
    @staticmethod
    def get_dashboard_stats_key(user_id: int) -> str:
        return CacheManager.get_key("dashboard_stats", user_id)
    
    @staticmethod
    def get_analytics_summary_key(user_id: int) -> str:
        return CacheManager.get_key("analytics_summary", user_id)
    
    @staticmethod
    def get_expenses_key(user_id: int, months: int = 12) -> str:
        return CacheManager.get_key("expenses", user_id, f"months:{months}")
    
    @staticmethod
    def get_categories_key(user_id: int) -> str:
        return CacheManager.get_key("categories", user_id)
    
    @staticmethod
    def get_forecast_key(user_id: int) -> str:
        return CacheManager.get_key("forecast", user_id)
    
    @staticmethod
    def invalidate_analytics_cache(user_id: int):
        """Инвалидирует весь кэш аналитики пользователя"""
        CacheManager.invalidate_user_cache(user_id, "analytics")
        CacheManager.invalidate_user_cache(user_id, "dashboard_stats")
        CacheManager.invalidate_user_cache(user_id, "expenses")
        CacheManager.invalidate_user_cache(user_id, "categories")
        CacheManager.invalidate_user_cache(user_id, "forecast")

class SubscriptionCache:
    """Кэширование данных подписок"""
    
    @staticmethod
    def get_subscriptions_key(user_id: int) -> str:
        return CacheManager.get_key("subscriptions", user_id)
    
    @staticmethod
    def get_notifications_key(user_id: int) -> str:
        return CacheManager.get_key("notifications", user_id)
    
    @staticmethod
    def invalidate_subscription_cache(user_id: int):
        """Инвалидирует кэш подписок пользователя"""
        CacheManager.invalidate_user_cache(user_id, "subscriptions")
        CacheManager.invalidate_user_cache(user_id, "notifications")
        # Также инвалидируем аналитику, так как она зависит от подписок
        AnalyticsCache.invalidate_analytics_cache(user_id)

# Глобальные настройки кэширования
CACHE_TTL = {
    'dashboard_stats': 300,      # 5 минут
    'analytics_summary': 600,    # 10 минут
    'expenses': 600,             # 10 минут
    'categories': 600,           # 10 минут
    'forecast': 900,             # 15 минут
    'subscriptions': 300,        # 5 минут
    'notifications': 300,        # 5 минут
} 