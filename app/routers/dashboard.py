from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription, Notification
from app.core.security import get_current_user
from app.core.cache import CacheManager, AnalyticsCache, SubscriptionCache, CACHE_TTL

router = APIRouter()

class DashboardStats(BaseModel):
    total_subscriptions: int
    active_subscriptions: int
    total_monthly_cost: float
    total_yearly_cost: float
    upcoming_bills: List[Dict[str, Any]]
    category_stats: List[Dict[str, Any]]

class NotificationResponse(BaseModel):
    id: int
    message: str
    is_read: bool
    created_at: datetime
    subscription_name: str
    
    class Config:
        from_attributes = True

class NotifyAllRequest(BaseModel):
    message: str

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить статистику дашборда"""
    
    print(f"Getting dashboard stats for user {current_user.id}")
    
    # Проверяем кэш
    cache_key = AnalyticsCache.get_dashboard_stats_key(current_user.id)
    cached_data = CacheManager.get_cache(cache_key)
    if cached_data:
        print(f"Returning cached dashboard stats for user {current_user.id}")
        return cached_data
    
    # Общая статистика
    total_subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).count()
    
    active_subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == True
    ).count()
    
    # Реальные расходы по всем активным подпискам
    all_active = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == True
    ).all()
    total_monthly_cost = 0
    total_yearly_cost = 0
    for sub in all_active:
        if sub.billing_cycle == "monthly":
            total_monthly_cost += sub.price
            total_yearly_cost += sub.price * 12
        elif sub.billing_cycle == "yearly":
            total_monthly_cost += sub.price / 12
            total_yearly_cost += sub.price
        elif sub.billing_cycle == "weekly":
            total_monthly_cost += sub.price * 4.33
            total_yearly_cost += sub.price * 52
        elif sub.billing_cycle == "daily":
            total_monthly_cost += sub.price * 30.44
            total_yearly_cost += sub.price * 365
        elif sub.billing_cycle == "once":
            pass  # разовые не учитываем
        else:
            total_monthly_cost += sub.price
            total_yearly_cost += sub.price * 12
    total_monthly_cost = round(total_monthly_cost, 2)
    total_yearly_cost = round(total_yearly_cost, 2)
    
    # Предстоящие платежи (в течение 30 дней)
    thirty_days_from_now = datetime.now() + timedelta(days=30)
    upcoming_bills = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == True,
        Subscription.next_billing_date <= thirty_days_from_now
    ).all()
    
    upcoming_bills_data = [
        {
            "id": sub.id,
            "name": sub.name,
            "price": sub.price,
            "currency": sub.currency,
            "next_billing_date": sub.next_billing_date,
            "days_until_billing": (sub.next_billing_date - datetime.now()).days
        }
        for sub in upcoming_bills
    ]
    
    # Статистика по категориям
    category_stats = db.query(
        func.coalesce(Subscription.category, '').label('category'),
        func.count(Subscription.id).label('count'),
        func.sum(Subscription.price).label('total_cost')
    ).filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == True
    ).group_by(func.coalesce(Subscription.category, '')).all()
    
    # Карта переводов категорий
    category_translations = {
        'streaming': 'Стриминг',
        'software': 'Программное обеспечение',
        'music': 'Музыка',
        'gaming': 'Игры',
        'education': 'Образование',
        'fitness': 'Фитнес',
        'news': 'Новости',
        'productivity': 'Продуктивность',
        'security': 'Безопасность',
        'storage': 'Хранилище',
        'other': 'Другое',
        '': 'Без категории'
    }
    
    print(f"Category stats from DB: {category_stats}")
    category_data = [
        {
            "category": category_translations.get(stat.category, "Без категории"),
            "count": stat.count,
            "total_cost": float(stat.total_cost) if stat.total_cost else 0
        }
        for stat in category_stats
    ]
    print(f"Processed category data: {category_data}")
    
    result = DashboardStats(
        total_subscriptions=total_subscriptions,
        active_subscriptions=active_subscriptions,
        total_monthly_cost=total_monthly_cost,
        total_yearly_cost=total_yearly_cost,
        upcoming_bills=upcoming_bills_data,
        category_stats=category_data
    )
    
    # Кэшируем результат
    CacheManager.set_cache(cache_key, result, CACHE_TTL['dashboard_stats'])
    
    return result

# --- Автогенерация напоминаний о платежах ---
NOTIFY_DAYS_BEFORE = 1  # За сколько дней до платежа напоминать

def generate_payment_notifications(user: User, db: Session):
    now = datetime.now()
    subs = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.is_active == True
    ).all()
    for sub in subs:
        days_left = (sub.next_billing_date - now).days
        if 0 <= days_left <= NOTIFY_DAYS_BEFORE:
            # Проверяем, есть ли уже такое уведомление
            exists = db.query(Notification).filter(
                Notification.user_id == user.id,
                Notification.subscription_id == sub.id,
                Notification.message.like(f'%{sub.name}%'),
                Notification.created_at >= now.replace(hour=0, minute=0, second=0, microsecond=0)
            ).first()
            if not exists:
                msg = f"Скоро платёж по подписке '{sub.name}' — {sub.next_billing_date.strftime('%d.%m.%Y')}"
                notif = Notification(
                    user_id=user.id,
                    subscription_id=sub.id,
                    message=msg
                )
                db.add(notif)
    db.commit()

# Вставляем вызов автогенерации в get_notifications
@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить уведомления пользователя"""
    
    # Проверяем кэш
    cache_key = SubscriptionCache.get_notifications_key(current_user.id)
    cached_data = CacheManager.get_cache(cache_key)
    if cached_data:
        return cached_data
    
    generate_payment_notifications(current_user, db)
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    result = [
        NotificationResponse(
            id=notif.id,
            message=notif.message,
            is_read=notif.is_read,
            created_at=notif.created_at,
            subscription_name=notif.subscription.name if notif.subscription_id else ""
        )
        for notif in notifications
    ]
    
    # Кэшируем результат
    CacheManager.set_cache(cache_key, result, CACHE_TTL['notifications'])
    
    return result

@router.delete("/notifications/clear")
async def clear_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(Notification).filter(Notification.user_id == current_user.id).delete()
    db.commit()
    
    # Инвалидируем кэш уведомлений
    SubscriptionCache.invalidate_subscription_cache(current_user.id)
    
    return {"message": "Все уведомления удалены"}

@router.post("/notify_all")
async def notify_all(
    req: NotifyAllRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только для администратора")
    users = db.query(User).all()
    for user in users:
        notif = Notification(
            user_id=user.id,
            subscription_id=None,
            message=req.message
        )
        db.add(notif)
    db.commit()
    
    # Инвалидируем кэш уведомлений для всех пользователей
    for user in users:
        SubscriptionCache.invalidate_subscription_cache(user.id)
    
    return {"message": f"Уведомление отправлено {len(users)} пользователям"}

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")
    
    notification.is_read = True
    db.commit()
    
    # Инвалидируем кэш уведомлений
    SubscriptionCache.invalidate_subscription_cache(current_user.id)
    
    return {"message": "Уведомление отмечено как прочитанное"} 