from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import calendar

from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.core.security import get_current_user
from app.core.cache import CacheManager, AnalyticsCache, CACHE_TTL

router = APIRouter()

class ExpenseData(BaseModel):
    month: str
    total: float
    count: int

class CategoryData(BaseModel):
    category: str
    total: float
    count: int
    percentage: float

class ForecastData(BaseModel):
    next_month: float
    trend: str  # "increasing", "decreasing", "stable"
    change_percentage: float

class AnalyticsResponse(BaseModel):
    expenses_by_month: List[ExpenseData]
    categories_data: List[CategoryData]
    forecast: ForecastData
    total_current_month: float
    average_monthly: float

@router.get("/expenses", response_model=List[ExpenseData])
async def get_expenses_by_month(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    months: int = 12
):
    """Получить расходы по месяцам за последние N месяцев"""
    
    print(f"Getting expenses for user {current_user.id}, months: {months}")
    
    # Проверяем кэш
    cache_key = AnalyticsCache.get_expenses_key(current_user.id, months)
    cached_data = CacheManager.get_cache(cache_key)
    if cached_data:
        print(f"Returning cached expenses data")
        return cached_data
    
    # Получаем данные за последние N месяцев
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    
    # Расчет расходов по месяцам - показываем все активные подписки
    expenses = db.query(
        func.date_trunc('month', Subscription.next_billing_date).label('month'),
        func.sum(Subscription.price).label('total'),
        func.count(Subscription.id).label('count')
    ).filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == True,
        Subscription.next_billing_date >= start_date
    ).group_by(
        func.date_trunc('month', Subscription.next_billing_date)
    ).order_by(
        func.date_trunc('month', Subscription.next_billing_date)
    ).all()
    
    result = [
        ExpenseData(
            month=expense.month.strftime("%Y-%m"),
            total=float(expense.total),
            count=expense.count
        )
        for expense in expenses
    ]
    
    print(f"Found {len(result)} expense records: {result}")
    
    # Кэшируем результат
    CacheManager.set_cache(cache_key, result, CACHE_TTL['expenses'])
    
    return result

@router.get("/categories", response_model=List[CategoryData])
async def get_categories_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить аналитику по категориям"""
    
    # Проверяем кэш
    cache_key = AnalyticsCache.get_categories_key(current_user.id)
    cached_data = CacheManager.get_cache(cache_key)
    if cached_data:
        return cached_data
    
    # Общая сумма расходов
    total_expenses = db.query(func.sum(Subscription.price)).filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == True
    ).scalar() or 0
    
    # Данные по категориям (включая подписки без категорий)
    categories = db.query(
        func.coalesce(Subscription.category, '').label('category'),
        func.sum(Subscription.price).label('total'),
        func.count(Subscription.id).label('count')
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
    
    result = []
    print(f"Categories from DB: {categories}")
    for cat in categories:
        percentage = (float(cat.total) / total_expenses * 100) if total_expenses > 0 else 0
        original_category = cat.category or ""
        translated_category = category_translations.get(original_category, "Без категории")
        print(f"Processing category: '{original_category}' -> '{translated_category}' (total: {cat.total}, count: {cat.count})")
        result.append(CategoryData(
            category=translated_category,
            total=float(cat.total),
            count=cat.count,
            percentage=round(percentage, 1)
        ))
    
    print(f"Final result: {result}")
    
    # Кэшируем результат
    CacheManager.set_cache(cache_key, result, CACHE_TTL['categories'])
    
    return result

@router.get("/forecast", response_model=ForecastData)
async def get_expense_forecast(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Прогноз расходов на следующий месяц"""
    
    # Проверяем кэш
    cache_key = AnalyticsCache.get_forecast_key(current_user.id)
    cached_data = CacheManager.get_cache(cache_key)
    if cached_data:
        return cached_data
    
    # Получаем данные за последние 3 месяца для анализа тренда
    three_months_ago = datetime.now() - timedelta(days=90)
    
    monthly_expenses = db.query(
        func.date_trunc('month', Subscription.next_billing_date).label('month'),
        func.sum(Subscription.price).label('total')
    ).filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == True,
        Subscription.next_billing_date >= three_months_ago
    ).group_by(
        func.date_trunc('month', Subscription.next_billing_date)
    ).order_by(
        func.date_trunc('month', Subscription.next_billing_date)
    ).all()
    
    if len(monthly_expenses) < 2:
        # Недостаточно данных для прогноза
        result = ForecastData(
            next_month=0,
            trend="stable",
            change_percentage=0
        )
    else:
        # Простой прогноз на основе среднего
        recent_expenses = [float(exp.total) for exp in monthly_expenses[-3:]]
        current_month = recent_expenses[-1] if recent_expenses else 0
        avg_expense = sum(recent_expenses) / len(recent_expenses)
        
        # Определяем тренд
        if len(recent_expenses) >= 2:
            if recent_expenses[-1] > recent_expenses[-2]:
                trend = "increasing"
                change = ((recent_expenses[-1] - recent_expenses[-2]) / recent_expenses[-2] * 100) if recent_expenses[-2] > 0 else 0
            elif recent_expenses[-1] < recent_expenses[-2]:
                trend = "decreasing"
                change = ((recent_expenses[-1] - recent_expenses[-2]) / recent_expenses[-2] * 100) if recent_expenses[-2] > 0 else 0
            else:
                trend = "stable"
                change = 0
        else:
            trend = "stable"
            change = 0
        
        result = ForecastData(
            next_month=round(avg_expense, 2),
            trend=trend,
            change_percentage=round(change, 1)
        )
    
    # Кэшируем результат
    CacheManager.set_cache(cache_key, result, CACHE_TTL['forecast'])
    
    return result

@router.get("/summary", response_model=AnalyticsResponse)
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить сводку аналитики"""
    
    print(f"Getting analytics summary for user {current_user.id}")
    
    try:
        # Проверяем кэш
        cache_key = AnalyticsCache.get_analytics_summary_key(current_user.id)
        cached_data = CacheManager.get_cache(cache_key)
        if cached_data:
            print(f"Returning cached analytics summary")
            return cached_data
    except Exception as e:
        print(f"Cache error in analytics summary: {e}")
        # Продолжаем без кэша
    
    try:
        # Расходы по месяцам
        expenses = await get_expenses_by_month(current_user, db, 6)
    except Exception as e:
        print(f"Error getting expenses: {e}")
        expenses = []
    
    try:
        # Данные по категориям
        categories = await get_categories_analytics(current_user, db)
    except Exception as e:
        print(f"Error getting categories: {e}")
        categories = []
    
    try:
        # Прогноз
        forecast = await get_expense_forecast(current_user, db)
    except Exception as e:
        print(f"Error getting forecast: {e}")
        forecast = ForecastData(next_month=0, trend="stable", change_percentage=0)
    
    try:
        # Текущий месяц - все активные подписки в текущем месяце
        current_month = datetime.now().replace(day=1)
        current_month_expenses = db.query(func.sum(Subscription.price)).filter(
            Subscription.user_id == current_user.id,
            Subscription.is_active == True,
            func.date_trunc('month', Subscription.next_billing_date) == func.date_trunc('month', current_month)
        ).scalar() or 0
    except Exception as e:
        print(f"Error getting current month expenses: {e}")
        current_month_expenses = 0
    
    try:
        # Средний месячный расход - все активные подписки
        monthly_subquery = db.query(
            func.date_trunc('month', Subscription.next_billing_date).label('month'),
            func.sum(Subscription.price).label('total')
        ).filter(
            Subscription.user_id == current_user.id,
            Subscription.is_active == True
        ).group_by(
            func.date_trunc('month', Subscription.next_billing_date)
        ).subquery()
        
        avg_monthly = db.query(func.avg(monthly_subquery.c.total)).scalar() or 0
    except Exception as e:
        print(f"Error getting average monthly: {e}")
        avg_monthly = 0
    
    result = AnalyticsResponse(
        expenses_by_month=expenses,
        categories_data=categories,
        forecast=forecast,
        total_current_month=float(current_month_expenses),
        average_monthly=float(avg_monthly)
    )
    
    print(f"Analytics summary result: current_month={current_month_expenses}, avg_monthly={avg_monthly}, expenses_count={len(expenses)}")
    
    try:
        # Кэшируем результат
        CacheManager.set_cache(cache_key, result, CACHE_TTL['analytics_summary'])
    except Exception as e:
        print(f"Error caching analytics summary: {e}")
    
    return result

@router.get("/export")
async def export_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    format: str = "json"
):
    """Экспорт аналитики в JSON/CSV"""
    try:
        analytics = await get_analytics_summary(current_user, db)
        
        if format.lower() == "json":
            return {
                "status": "success",
                "format": "json",
                "data": analytics,
                "exported_at": datetime.now().isoformat(),
                "user_id": current_user.id
            }
        elif format.lower() == "csv":
            # CSV экспорт с UTF-8 кодировкой
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Заголовки
            writer.writerow(['Месяц', 'Расходы (₽)', 'Количество подписок'])
            
            # Данные по месяцам
            for expense in analytics.expenses_by_month:
                writer.writerow([expense.month, expense.total, expense.count])
            
            # Пустая строка
            writer.writerow([])
            
            # Категории
            writer.writerow(['Категория', 'Расходы (₽)', 'Процент'])
            for category in analytics.categories_data:
                writer.writerow([category.category, category.total, f"{category.percentage}%"])
            
            csv_content = output.getvalue()
            output.close()
            
            # Добавляем BOM для UTF-8
            utf8_bom = '\ufeff'
            csv_content_with_bom = utf8_bom + csv_content
            
            from fastapi.responses import Response
            return Response(
                content=csv_content_with_bom,
                media_type="text/csv; charset=utf-8",
                headers={
                    "Content-Disposition": f"attachment; filename=analytics_{datetime.now().strftime('%Y%m%d')}.csv",
                    "Content-Type": "text/csv; charset=utf-8"
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Неподдерживаемый формат экспорта")
            
    except Exception as e:
        print(f"Error in export analytics: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при экспорте аналитики") 