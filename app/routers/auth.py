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

def generate_verification_code():
    return secrets.token_hex(3)  # Générer un code de vérification


conf = ConnectionConfig(
    MAIL_USERNAME ="benmoumenfawzi@gmail.com",
    MAIL_PASSWORD = "sxrm ddul wqxa btae",
    MAIL_FROM = "benmoumenfawzi@gmail.com",
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)


def html(number) : 
    return f"""
<h1> Votre code d'authentification est : {number} </h1> 
"""



@router.post("/email")
async def simple_send(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    
    if not user or not utils.verify_pwd(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid credentials')
    
    if not user.state :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='account has been blocked')
    
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    if not user.TFA:
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "detail": "Single Factor Authentication",
                "access_token": access_token
            }
        )

    # Generate verification code
    verification_code = generate_verification_code()
    user.verification_code = verification_code
    user.code_expiry = datetime.utcnow() + timedelta(minutes=10)  # Code valid for 10 minutes
    db.commit()
    
    message = MessageSchema(
        subject="OTP",
        recipients=[user.email],
        body=html(verification_code),
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
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

    return {"access_token": access_token}

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
