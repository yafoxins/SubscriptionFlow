from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.core.security import get_current_user
from app.core.calendar_integration import CalendarIntegration

router = APIRouter()

class GoogleCalendarSetup(BaseModel):
    credentials_json: str

class OutlookCalendarSetup(BaseModel):
    access_token: str

class CalendarEventResponse(BaseModel):
    source: str
    id: str
    title: str
    description: str
    start: str
    end: str
    color: Optional[str] = None

# Глобальный экземпляр интеграции с календарями
calendar_integration = CalendarIntegration()

@router.post("/google/setup")
async def setup_google_calendar(
    setup_data: GoogleCalendarSetup,
    current_user: User = Depends(get_current_user)
):
    """Настройка интеграции с Google Calendar"""
    result = calendar_integration.setup_google_calendar(setup_data.credentials_json)
    return result

@router.post("/outlook/setup")
async def setup_outlook_calendar(
    setup_data: OutlookCalendarSetup,
    current_user: User = Depends(get_current_user)
):
    """Настройка интеграции с Outlook Calendar"""
    result = calendar_integration.setup_outlook_calendar(setup_data.access_token)
    return result

@router.post("/subscriptions/{subscription_id}/add-to-google")
async def add_subscription_to_google_calendar(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Добавить подписку в Google Calendar"""
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")
    
    result = calendar_integration.add_subscription_to_google_calendar(subscription)
    return result

@router.post("/subscriptions/{subscription_id}/add-to-outlook")
async def add_subscription_to_outlook_calendar(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Добавить подписку в Outlook Calendar"""
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")
    
    result = calendar_integration.add_subscription_to_outlook_calendar(subscription)
    return result

@router.get("/events")
async def get_calendar_events(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Получить события из календарей"""
    # По умолчанию показываем события за текущий месяц
    if not start_date:
        start_date = datetime.now().replace(day=1)
    else:
        start_date = datetime.fromisoformat(start_date)
    
    if not end_date:
        end_date = (start_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    else:
        end_date = datetime.fromisoformat(end_date)
    
    events = calendar_integration.get_calendar_events(start_date, end_date)
    return events

@router.post("/subscriptions/{subscription_id}/sync")
async def sync_subscription_to_calendars(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Синхронизировать подписку со всеми подключенными календарями"""
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Подписка не найдена")
    
    results = {}
    
    # Пытаемся добавить в Google Calendar
    try:
        google_result = calendar_integration.add_subscription_to_google_calendar(subscription)
        results['google'] = google_result
    except Exception as e:
        results['google'] = {
            'success': False,
            'message': f'Ошибка Google Calendar: {str(e)}'
        }
    
    # Пытаемся добавить в Outlook Calendar
    try:
        outlook_result = calendar_integration.add_subscription_to_outlook_calendar(subscription)
        results['outlook'] = outlook_result
    except Exception as e:
        results['outlook'] = {
            'success': False,
            'message': f'Ошибка Outlook Calendar: {str(e)}'
        }
    
    return {
        'subscription_id': subscription_id,
        'results': results
    } 