from fastapi import FastAPI, File, UploadFile, APIRouter, Depends, HTTPException, Response, status
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from pathlib import Path
from .. import oauth2, models, utils, schemas
from ..database import get_db
from sqlalchemy.orm import Session, joinedload
from base64 import b64decode
from cryptography.hazmat.primitives import padding
from sqlalchemy import func  # Importer func de SQLAlchemy pour les fonctions d'agrégation
from sqlalchemy import cast, Integer,Float,text
from collections import Counter


router = APIRouter(
    prefix="/settings",
    tags=['Settings']
)

@router.put('/pwd_rotation',status_code=status.HTTP_200_OK)
def update_pwd_rotation(time : schemas.PasswordRotationUpdate, db: Session = Depends(get_db), current_admin = Depends(oauth2.get_current_admin)) : 
    admin_parameters= db.query(models.Admin_Parameter).first()
    if not admin_parameters : 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="This admin has no parameters")
    
    admin_parameters.pwd_rotation = time.value
    db.commit()
    db.refresh(admin_parameters)
    return {}

@router.put('/login_attempts',status_code=status.HTTP_200_OK)
def update_login_attempts(time : schemas.PasswordRotationUpdate, db: Session = Depends(get_db), current_admin = Depends(oauth2.get_current_admin)) : 
    admin_parameters= db.query(models.Admin_Parameter).first()
    if not admin_parameters : 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="This admin has no parameters")
    
    admin_parameters.login_attempt = time.value
    db.commit()
    db.refresh(admin_parameters)
    return {}

@router.post('/extension', status_code=status.HTTP_200_OK)
def add_extension(extension: schemas.AddExtensionSchema, db: Session = Depends(get_db), current_admin: int = Depends(oauth2.get_current_admin)):
    # Vérifier si l'extension existe déjà
    existing_extension = db.query(models.Extension).filter(models.Extension.extension == extension.ext).first()
    if existing_extension:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This extension already exists.")

    # Créer une nouvelle instance de l'extension
    new_extension = models.Extension(extension=extension.ext)
    
    # Ajouter la nouvelle extension à la base de données
    db.add(new_extension)
    db.commit()
    db.refresh(new_extension)

    return {"detail": "Extension added successfully", "extension": new_extension.extension}



@router.post('/domain', status_code=status.HTTP_200_OK)
def add_domain(domain: schemas.AddDomainSchema, db: Session = Depends(get_db), current_admin: int = Depends(oauth2.get_current_admin)):
    # Vérifier si le domaine existe déjà
    existing_domain = db.query(models.Domain).filter(models.Domain.domain == domain.domain).first()
    if existing_domain:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This domain already exists.")

    # Créer une nouvelle instance de domaine
    new_domain = models.Domain(domain=domain.domain)
    
    # Ajouter le nouveau domaine à la base de données
    db.add(new_domain)
    db.commit()
    db.refresh(new_domain)

    return {"detail": "Domain added successfully", "domain": new_domain.domain}

@router.get('/', response_model=schemas.AdminParametersResponse, status_code=status.HTTP_200_OK)
def get_settings(db: Session = Depends(get_db), current_admin: int = Depends(oauth2.get_current_admin)):
    # Récupérer les paramètres administratifs
    admin_parameters = db.query(models.Admin_Parameter).first()
    if not admin_parameters:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin parameters not found.")

    # Récupérer les extensions
    extensions = db.query(models.Extension).all()
    extension_list = [schemas.ExtensionResponse(id=ext.id, extension=ext.extension) for ext in extensions]

    # Récupérer les domaines
    domains = db.query(models.Domain).all()
    domain_list = [schemas.DomainResponse(id=dom.id, domain=dom.domain) for dom in domains]

    # Créer la réponse
    response = schemas.AdminParametersResponse(
        pwd_rotation=admin_parameters.pwd_rotation,
        login_attempt=admin_parameters.login_attempt,
        extensions=extension_list,
        domains=domain_list
    )
    
    return response