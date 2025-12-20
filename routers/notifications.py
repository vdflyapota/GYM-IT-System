# routers/notifications.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import notification_models
import schemas

router = APIRouter(prefix="/notifications", tags=["Notifications & Audit"])

@router.post("/broadcast")
def send_broadcast(message: str, db: Session = Depends(get_db)):
    """Simulates sending an email to everyone. Logs the action."""
    # 1. Create Audit Log
    log = notification_models.AuditLog(action="BROADCAST", details=message)
    db.add(log)
    
    # 2. (Simulated) Create notification for user ID 1
    notif = notification_models.Notification(user_id=1, message=message)
    db.add(notif)
    
    db.commit()
    return {"status": "Broadcast sent and logged"}

@router.get("/my-notifications", response_model=list[schemas.NotificationResponse])
def get_my_notifications(user_id: int = 1, db: Session = Depends(get_db)):
    return db.query(notification_models.Notification).filter(notification_models.Notification.user_id == user_id).all()
