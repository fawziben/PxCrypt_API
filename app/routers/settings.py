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

@router.delete('/extension', status_code=status.HTTP_200_OK)
def delete_extension_by_name(extension: schemas.DeleteExtensionSchema, db: Session = Depends(get_db), current_admin: int = Depends(oauth2.get_current_admin)):
    extension_to_delete = db.query(models.Extension).filter(models.Extension.extension == extension.ext).first()
    if not extension_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extension not found.")
    db.delete(extension_to_delete)
    db.commit()
    return {"detail": "Extension deleted successfully"}


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

@router.delete('/domain', status_code=status.HTTP_200_OK)
def delete_domain_by_name(domain: schemas.DeleteDomainSchema, db: Session = Depends(get_db), current_admin: int = Depends(oauth2.get_current_admin)):
    domain_to_delete = db.query(models.Domain).filter(models.Domain.domain == domain.domain).first()
    if not domain_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found.")
    db.delete(domain_to_delete)
    db.commit()
    return {"detail": "Domain deleted successfully"}


@router.put("/all_domains")
def update_all_domains_state(db: Session = Depends(get_db),current_admin: int = Depends(oauth2.get_current_admin)):
    try:
        # Récupérer l'enregistrement unique dans Admin_Parameter
        param = db.query(models.Admin_Parameter).first()
        if not param:
            raise HTTPException(status_code=404, detail="Admin parameters not found")

        # Mettre à jour l'état de all_domains
        param.all_domains = not param.all_domains
        db.commit()
        db.refresh(param)
        return {"message": "all_domains state updated successfully", "all_domains": param.all_domains}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fonction pour modifier l'état de all_extensions
@router.put("/all_extensions")
def update_all_extensions_state(db: Session = Depends(get_db), current_admin: int = Depends(oauth2.get_current_admin)):
    try:
        # Récupérer l'enregistrement unique dans Admin_Parameter
        param = db.query(models.Admin_Parameter).first()
        print (param)
        if not param:
            raise HTTPException(status_code=404, detail="Admin parameters not found")

        # Mettre à jour l'état de all_extensions
        param.all_extensions = not param.all_extensions
        db.commit()
        db.refresh(param)
        return {"message": "all_extensions state updated successfully", "all_extensions": param.all_extensions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        all_extensions=admin_parameters.all_extensions,
        all_domains=admin_parameters.all_domains,
        extensions=extension_list,
        domains=domain_list
    )
    
    return response

@router.put("/verify_extensions")
def verify_allowed_extensions(
    ext: str,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user)
):
    try:
        # Print the extension being checked
        print(f"Checking extension: {ext}")
        
        # Retrieve the admin parameters
        param = db.query(models.Admin_Parameter).first()
        if not param:
            print("Admin parameters not found in the database.")
            raise HTTPException(status_code=404, detail="Admin parameters not found")
        
        # Log the state of 'all_extensions'
        print(f"All extensions allowed: {param.all_extensions}")
        
        # Check the state of 'all_extensions'
        if param.all_extensions:
            # If 'all_extensions' is True, return 200 status
            print("All extensions are allowed.")
            return {"message": "All extensions are allowed", "status_code": 200}

        # If 'all_extensions' is False, verify if 'ext' is in the extensions table
        extension_exists = db.query(models.Extension).filter(models.Extension.extension == ext).first()
        
        if extension_exists:
            # Extension is allowed
            print(f"Extension '{ext}' is allowed.")
            return {"message": f"Extension '{ext}' is allowed", "status_code": 200}
        else:
            # Extension is not allowed
            print(f"Extension '{ext}' is not allowed.")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Extension is not allowed")

    except HTTPException as he:
        # Handle known exceptions gracefully
        print(f"HTTP Exception: {he.detail}")
        raise he

    except Exception as e:
        # Catch any unexpected exceptions
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
