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
    prefix="/stats",
    tags=['Statistics']
)
@router.get('/ufiles/{id}', status_code=status.HTTP_200_OK, response_model=dict)
def get_user_files_count(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)): 
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user with this index found")

    nbfiles = db.query(models.Ufile).filter(models.Ufile.id_owner == id).count()
    return {'count': nbfiles}


@router.get('/rfiles/{id}', status_code=status.HTTP_200_OK, response_model=dict)
def get_user_files_count(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)): 
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user with this index found")

    nbfiles = db.query(models.Sfile).filter(models.Sfile.id_receiver == id).count()
    return {'count': nbfiles}


@router.get('/sfiles/{id}', status_code=status.HTTP_200_OK)
def get_file_count(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user with this index found")

    file_count = db.query(models.Sfile) \
        .join(models.Ufile, models.Sfile.id_file == models.Ufile.id) \
        .filter(models.Ufile.id_owner == id) \
        .count()

    return {'count': file_count}





@router.get('/file-counts/{id}', status_code=status.HTTP_200_OK, response_model=schemas.FileCountsResponse)
def get_file_counts(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # Vérifiez si l'utilisateur existe
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user with this index found")

    # Comptez les fichiers de l'utilisateur
    user_files_count = db.query(models.Ufile).filter(models.Ufile.id_owner == id).count()

    # Comptez les fichiers reçus par l'utilisateur
    received_files_count = db.query(models.Sfile).filter(models.Sfile.id_receiver == id).count()

    # Comptez les fichiers partagés par l'utilisateur
    shared_files_count = db.query(models.Sfile) \
        .join(models.Ufile, models.Sfile.id_file == models.Ufile.id) \
        .filter(models.Ufile.id_owner == id) \
        .count()

    # Calculez la taille totale des fichiers uploadés par l'utilisateur (en octets)
    total_uploaded_size = db.query(func.sum(cast(models.Ufile.size, Integer))) \
        .filter(models.Ufile.id_owner == id) \
        .scalar() or 0  # Utiliser 0 comme valeur par défaut si aucun fichier n'est trouvé

    print(total_uploaded_size)
    return {
        'user_files_count': user_files_count,
        'received_files_count': received_files_count,
        'shared_files_count': shared_files_count,
        'total_uploaded_size': total_uploaded_size  # Ajouter la taille totale des fichiers uploadés
    }



@router.get('/server_stats', status_code=status.HTTP_200_OK)
def get_server_stats(db: Session = Depends(get_db), current_admin=Depends(oauth2.get_current_admin)):
    # Nombre total d'utilisateurs
    total_users = db.query(models.User).count()

    # Nombre d'utilisateurs actifs
    active_users = db.query(models.User).filter(models.User.state == True).count()

    # Nombre d'utilisateurs bloqués
    blocked_users = db.query(models.User).filter(models.User.state == False).count()

    # Taille totale des fichiers stockés
    total_storage_used = db.query(func.sum(func.cast(models.Ufile.size, Float))).scalar() or 0


    return {
        'total_users': total_users,
        'active_users': active_users,
        'blocked_users': blocked_users,
        'total_storage_used': total_storage_used
    }


@router.get("/user_storage", response_model=list[schemas.UserStorageResponse])
async def get_user_storage(db: Session = Depends(get_db)):
    # Récupérer les utilisateurs avec la quantité de stockage utilisée
    users = db.query(models.User).all()
    
    user_storage_list = []
    
    for user in users:
        # Calculer le stockage total utilisé par chaque utilisateur
        storage_used = db.query(func.sum(cast(models.Ufile.size, Float))).filter(models.Ufile.id_owner == user.id).scalar() or 0
        user_storage_list.append(schemas.UserStorageResponse(
            name=user.first_name + ' ' +user.last_name ,
            storage_used=storage_used
        ))
    
    return user_storage_list

@router.get("/file_extensions", response_model=list[schemas.FileExtensionCountResponse])
async def get_file_extensions(db: Session = Depends(get_db)):
    # Exécuter une requête pour récupérer les noms des fichiers
    query = text("""
        SELECT name FROM ufiles
    """)
    result = db.execute(query)
    filenames = [row.name for row in result.fetchall()]

    # Extraire les extensions des noms de fichiers
    extensions = []
    for filename in filenames:
        parts = filename.rsplit('.', 2)  # Diviser en deux parties à partir du dernier point
        if len(parts) > 1:
            extension = parts[-2]  # Obtenir l'extension juste avant la dernière partie
            extensions.append(extension)

    # Compter les occurrences de chaque extension
    extension_counts = Counter(extensions)

    # Transformer les résultats en une liste de réponses
    extensions_list = [
        schemas.FileExtensionCountResponse(extension=ext, count=count)
        for ext, count in extension_counts.items()
    ]

    return extensions_list