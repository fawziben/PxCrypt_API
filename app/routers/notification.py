from datetime import datetime, timedelta
from fastapi import Response, status, HTTPException, Depends,APIRouter, UploadFile, File, Body
from .. import models,schemas,utils,oauth2
from ..database import get_db
from sqlalchemy.orm import Session
import shutil
import os
import base64
from sqlalchemy.orm import joinedload

router = APIRouter(
    prefix="/notification",
    tags=['Notification']
)

@router.get('/', status_code=status.HTTP_200_OK)
async def get_user_notifications(
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    # Vérifier si l'utilisateur existe
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Récupérer les notifications de l'utilisateur avec les informations du notifier
    notifications = db.query(models.User_Notification).\
        options(joinedload(models.User_Notification.notifier)).\
        filter(models.User_Notification.id_user == current_user.id).\
        all()

    # Formater la réponse pour inclure l'email du notifier
    response = []
    for notification in notifications:
        response.append({
            "id": notification.id,
            "notifier_email": notification.notifier.email,  # Inclure l'email du notifier
            "type": notification.type,    # Inclure d'autres détails si nécessaire
            "unread": notification.unread,    # Inclure d'autres détails si nécessaire
            "date": notification.date,    # Inclure d'autres détails si nécessaire
            "file_name" : notification.file_name

        })


    return response

@router.put('/', status_code=status.HTTP_200_OK)
def mark_all_as_read(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    # Requête pour récupérer toutes les notifications non lues de l'utilisateur actuel
    notifs = db.query(models.User_Notification).filter(
        models.User_Notification.id_user == current_user.id,  # Filtrer par l'utilisateur actuel
        models.User_Notification.unread == True  # Filtrer seulement les notifications non lues
    ).all()

    if not notifs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No notifications found")

    # Marquer toutes les notifications comme lues
    for notif in notifs:
        notif.unread = False
        db.commit()
        db.refresh(notif)

    return {"message": "All notifications marked as read"}

@router.put('/{id}', status_code=status.HTTP_200_OK)
def mark_as_read(id: int, db: Session= Depends(get_db), current_user= Depends(oauth2.get_current_user)):
    notif = db.query(models.User_Notification).filter(models.User_Notification.id == id).first()

    if notif is None : 
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notif.unread = False
    db.commit()
    db.refresh(notif)
    return{}