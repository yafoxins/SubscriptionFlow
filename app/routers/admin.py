from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription, Notification
from app.core.security import get_current_user
from pydantic import BaseModel

router = APIRouter()

@router.get("/dashboard", tags=["admin"])
async def admin_dashboard(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только для администратора")
    return {"message": "Admin dashboard"}

@router.get("/stats", tags=["admin"])
async def admin_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только для администратора")
    users_count = db.query(User).count()
    subs_count = db.query(Subscription).count()
    active_subs = db.query(Subscription).filter(Subscription.is_active == True).count()
    inactive_subs = db.query(Subscription).filter(Subscription.is_active == False).count()
    notifications_count = db.query(Notification).count()
    admins_count = db.query(User).filter(User.is_admin == True).count()
    return {
        "users": users_count,
        "subscriptions": subs_count,
        "active_subscriptions": active_subs,
        "inactive_subscriptions": inactive_subs,
        "notifications": notifications_count,
        "admins": admins_count
    }

class AddAdminRequest(BaseModel):
    identifier: str  # email или username

@router.get("/list", tags=["admin"])
async def admin_list(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только для администратора")
    admins = db.query(User).filter(User.is_admin == True).all()
    return [{"id": u.id, "username": u.username, "email": u.email} for u in admins]

@router.post("/add", tags=["admin"])
async def add_admin(req: AddAdminRequest = Body(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Только для администратора")
    user = db.query(User).filter((User.email == req.identifier) | (User.username == req.identifier)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="Пользователь уже админ")
    user.is_admin = True
    db.commit()
    return {"message": "Пользователь назначен админом"} 