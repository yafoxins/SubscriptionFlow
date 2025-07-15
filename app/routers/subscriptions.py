from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.core.security import get_current_user
from app.core.cache import CacheManager, SubscriptionCache, AnalyticsCache, CACHE_TTL
from app.core.smart_categories import SmartCategoryDetector
from app.core.calendar_integration import CalendarIntegration

router = APIRouter()

class SubscriptionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "RUB"
    billing_cycle: str
    next_billing_date: datetime
    category: Optional[str] = None
    website_url: Optional[str] = None

class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    billing_cycle: Optional[str] = None
    next_billing_date: Optional[datetime] = None
    category: Optional[str] = None
    website_url: Optional[str] = None
    is_active: Optional[bool] = None

class SubscriptionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    currency: str
    billing_cycle: str
    next_billing_date: datetime
    is_active: bool
    category: Optional[str]
    website_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

def shift_next_billing_date(subscription):
    """
    Автоматически сдвигает next_billing_date, если она в прошлом, согласно billing_cycle.
    Возвращает True, если дата была сдвинута.
    """
    now = datetime.now()
    updated = False
    while subscription.next_billing_date and subscription.next_billing_date < now:
        if subscription.billing_cycle == 'monthly':
            subscription.next_billing_date += timedelta(days=30)
        elif subscription.billing_cycle == 'yearly':
            subscription.next_billing_date += timedelta(days=365)
        elif subscription.billing_cycle == 'weekly':
            subscription.next_billing_date += timedelta(days=7)
        elif subscription.billing_cycle == 'daily':
            subscription.next_billing_date += timedelta(days=1)
        else:
            break
        updated = True
    return updated

@router.get("/categories")
async def get_categories():
    """Получить все доступные категории"""
    try:
        categories = SmartCategoryDetector.get_all_categories()
        print(f"Returning {len(categories)} categories")
        return categories
    except Exception as e:
        print(f"Error getting categories: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Ошибка при получении категорий")

@router.get("/test-category-detection")
async def test_category_detection():
    """Тестовый endpoint для проверки работы детектора категорий"""
    try:
        test_cases = [
            ("Netflix", "Streaming service"),
            ("Adobe Photoshop", "Photo editing software"),
            ("Spotify", "Music streaming"),
            ("Xbox Game Pass", "Gaming subscription")
        ]
        
        results = []
        for name, description in test_cases:
            detected = SmartCategoryDetector.detect_category(name, description)
            results.append({
                "name": name,
                "description": description,
                "detected_category": detected
            })
        
        return {"test_results": results}
    except Exception as e:
        print(f"Error in test_category_detection: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Ошибка в тестовом endpoint")

class CategoryDetectionRequest(BaseModel):
    name: str
    description: Optional[str] = None

@router.post("/detect-category")
async def detect_category(request: CategoryDetectionRequest):
    """Определить категорию по названию и описанию"""
    try:
        print(f"Received detect_category request: name='{request.name}', description='{request.description}'")
        
        if not request.name or not request.name.strip():
            print("Empty name provided")
            raise HTTPException(status_code=422, detail="Название подписки обязательно")
        
        detected = SmartCategoryDetector.detect_category(request.name, request.description)
        print(f"Detected category: {detected}")
        
        if detected:
            info = SmartCategoryDetector.get_category_info(detected)
            result = {
                "category": detected,
                "name": info["name"],
                "icon": info["icon"]
            }
            print(f"Returning result: {result}")
            return result
        else:
            print("No category detected")
            return {"category": None}
    except Exception as e:
        print(f"Error in detect_category: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Ошибка при определении категории")

@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать новую подписку"""
    # Умное определение категории если не указана
    if not subscription_data.category:
        detected_category = SmartCategoryDetector.detect_category(
            subscription_data.name, 
            subscription_data.description
        )
        if detected_category:
            subscription_data.category = detected_category
    
    db_subscription = Subscription(
        user_id=current_user.id,
        **subscription_data.model_dump()
    )
    
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    
    # Инвалидируем кэш подписок и аналитики
    print(f"Invalidating cache for user {current_user.id} after subscription creation")
    SubscriptionCache.invalidate_subscription_cache(current_user.id)
    AnalyticsCache.invalidate_analytics_cache(current_user.id)
    
    # Принудительно очищаем все связанные кэши
    try:
        CacheManager.invalidate_user_cache(current_user.id)
        print(f"All cache cleared for user {current_user.id}")
    except Exception as e:
        print(f"Error clearing cache: {e}")
    
    return SubscriptionResponse(
        id=db_subscription.id,
        name=db_subscription.name,
        description=db_subscription.description,
        price=db_subscription.price,
        currency=db_subscription.currency,
        billing_cycle=db_subscription.billing_cycle,
        next_billing_date=db_subscription.next_billing_date,
        is_active=db_subscription.is_active,
        category=db_subscription.category,
        website_url=db_subscription.website_url,
        created_at=db_subscription.created_at
    )

@router.get("/", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить все подписки пользователя"""
    
    # Проверяем кэш
    cache_key = SubscriptionCache.get_subscriptions_key(current_user.id)
    cached_data = CacheManager.get_cache(cache_key)
    if cached_data:
        return cached_data
    
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).order_by(Subscription.created_at.desc()).all()
    
    result = [
        SubscriptionResponse(
            id=sub.id,
            name=sub.name,
            description=sub.description,
            price=sub.price,
            currency=sub.currency,
            billing_cycle=sub.billing_cycle,
            next_billing_date=sub.next_billing_date,
            is_active=sub.is_active,
            category=sub.category,
            website_url=sub.website_url,
            created_at=sub.created_at
        )
        for sub in subscriptions
    ]
    
    # Кэшируем результат
    CacheManager.set_cache(cache_key, result, CACHE_TTL['subscriptions'])
    
    return result

@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить конкретную подписку"""
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")
    
    return SubscriptionResponse(
        id=subscription.id,
        name=subscription.name,
        description=subscription.description,
        price=subscription.price,
        currency=subscription.currency,
        billing_cycle=subscription.billing_cycle,
        next_billing_date=subscription.next_billing_date,
        is_active=subscription.is_active,
        category=subscription.category,
        website_url=subscription.website_url,
        created_at=subscription.created_at
    )

@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    subscription_data: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить подписку"""
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")
    
    # Обновляем только переданные поля
    update_data = subscription_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subscription, field, value)
    
    db.commit()
    db.refresh(subscription)
    
    # Инвалидируем кэш подписок и аналитики
    print(f"Invalidating cache for user {current_user.id} after subscription update")
    SubscriptionCache.invalidate_subscription_cache(current_user.id)
    AnalyticsCache.invalidate_analytics_cache(current_user.id)
    
    # Принудительно очищаем все связанные кэши
    try:
        CacheManager.invalidate_user_cache(current_user.id)
        print(f"All cache cleared for user {current_user.id}")
    except Exception as e:
        print(f"Error clearing cache: {e}")
    
    return SubscriptionResponse(
        id=subscription.id,
        name=subscription.name,
        description=subscription.description,
        price=subscription.price,
        currency=subscription.currency,
        billing_cycle=subscription.billing_cycle,
        next_billing_date=subscription.next_billing_date,
        is_active=subscription.is_active,
        category=subscription.category,
        website_url=subscription.website_url,
        created_at=subscription.created_at
    )

@router.delete("/{subscription_id}")
async def delete_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить подписку"""
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")
    
    db.delete(subscription)
    db.commit()
    
    # Инвалидируем кэш подписок и аналитики
    print(f"Invalidating cache for user {current_user.id} after subscription deletion")
    SubscriptionCache.invalidate_subscription_cache(current_user.id)
    AnalyticsCache.invalidate_analytics_cache(current_user.id)
    
    # Принудительно очищаем все связанные кэши
    try:
        CacheManager.invalidate_user_cache(current_user.id)
        print(f"All cache cleared for user {current_user.id}")
    except Exception as e:
        print(f"Error clearing cache: {e}")
    
    return {"message": "Подписка успешно удалена"} 