from fastapi import Response, status, HTTPException, Depends, APIRouter, BackgroundTasks
from .. import models, schemas, utils, oauth2
from .. import database
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from datetime import datetime, timedelta
import secrets
from pydantic import BaseModel, EmailStr
from pathlib import Path
from starlette.responses import JSONResponse
from typing import List

router = APIRouter(tags=['Authentication'])

@router.post("/email")
async def simple_send(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User with this email does not exist')
    
    if not user.state :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='account has been blocked')
    
    params= db.query(models.Admin_Parameter).first()
    print(user.attempts)
    if not utils.verify_pwd(user_credentials.password, user.password):  
        user.attempts += 1
        if(int(params.login_attempt) <= int(user.attempts)) :
            user.state=False 
            admin = db.query(models.Admin).first()
            utils.notify_admin(admin.id,db,"total_attempts_reached",user.id,params.login_attempt)

        db.commit()
        db.refresh(user)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    if not user.TFA:
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "detail": "Single Factor Authentication",
                "access_token": access_token,
                "user_id" : user.id
            }
        )

    # Generate verification code
    verification_code = utils.generate_verification_code()
    user.verification_code = verification_code
    user.code_expiry = datetime.utcnow() + timedelta(minutes=10)  # Code valid for 10 minutes
    db.commit()
    await utils.send_email(user.email,verification_code)
    return {"message": "email has been sent"}

@router.post('/verify-code')
def verify_code(user_credentials : schemas.UserVerify, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    if not user or user.verification_code != user_credentials.code or user.code_expiry < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired verification code'
        )

    # Clear verification code after successful verification
    user.verification_code = None
    user.code_expiry = None
    db.commit()

    # Generate access token
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    print (user.id)
    return {"access_token": access_token,  "user_id" : user.id}

@router.post('/login')
def login(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)): 
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    
    if not user or not utils.verify_pwd(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid credentials')
    
    access_token = oauth2.create_access_token(data={"user_id": user.id})    
    return {"access_token": access_token}

@router.put('/reset/password', status_code=status.HTTP_200_OK)
def reset_password(user_credentials: schemas.PasswordReset, db: Session = Depends(database.get_db), current_user = Depends(oauth2.get_current_user)):
    # Rechercher l'utilisateur par email
    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    # Vérifier si l'utilisateur existe et si l'ancien mot de passe est correct
    if not user or not utils.verify_pwd(user_credentials.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid credentials'
        )

    # Hacher le nouveau mot de passe
    hashed_new_password = utils.hash_pwd(user_credentials.new_password)

    # Mettre à jour le mot de passe dans la base de données
    user.password = hashed_new_password
    db.commit()

    # Créer un nouveau token d'accès
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {}

@router.post('/admin/login')
def login(user_credentials: schemas.AdminLogin, db: Session = Depends(database.get_db)): 
    user = db.query(models.Admin).filter(models.Admin.username == user_credentials.username).first()
    print(user)
    print(user_credentials)
    
    if not user or (user_credentials.password != user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid credentials')
    
    access_token = oauth2.create_access_token(data={"user_id": user.id})    
    return {"access_token": access_token}



@router.post("/admin/email")
async def simple_send(user_credentials: schemas.AdminLogin, db: Session = Depends(database.get_db)):
    admin = db.query(models.Admin).filter(models.Admin.username == user_credentials.username).first()
    
    if not admin or not (user_credentials.password == admin.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid credentials')
    
    # Generate verification code
    verification_code = utils.generate_verification_code()
    admin.verification_code = verification_code
    admin.code_expiry = datetime.utcnow() + timedelta(minutes=10)  # Code valid for 10 minutes
    db.commit()
    
    await utils.send_email(admin.username,verification_code)
    return {"message": "email has been sent"}


@router.post('/admin/verify-code')
def verify_code(user_credentials : schemas.UserVerify, db: Session = Depends(database.get_db)):
    admin = db.query(models.Admin).filter(models.Admin.username == user_credentials.email).first()

    if not admin or admin.verification_code != user_credentials.code or admin.code_expiry < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired verification code'
        )

    # Clear verification code after successful verification
    admin.verification_code = None
    admin.code_expiry = None
    db.commit()

    # Generate access token
    access_token = oauth2.create_access_token(data={"user_id": admin.id})
    print (admin.id)
    return {"access_token": access_token,  "user_id" : admin.id}