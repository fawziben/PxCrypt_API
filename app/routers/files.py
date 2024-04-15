from fastapi import FastAPI, File, UploadFile, APIRouter, Depends, HTTPException, Response, status
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from pathlib import Path
from .. import oauth2, models
from ..database import get_db
from sqlalchemy.orm import Session
from base64 import b64decode
from cryptography.hazmat.primitives import padding

router = APIRouter(
    prefix="/files",
    tags=['Files']
)

@router.post('/share', status_code=status.HTTP_200_OK)
async def share_with(file: UploadFile = File(...), db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    encrypted_content_b64 = await file.read()

    # Créer le répertoire s'il n'existe pas
    Path('test').mkdir(parents=True, exist_ok=True)

    # Chemin complet du fichier
    file_path = os.path.join('test', file.filename)

    # Écrire le contenu du fichier dans le répertoire
    with open(file_path, "wb") as f:
        f.write(encrypted_content_b64)

    return True

@router.post('/upload', status_code=status.HTTP_200_OK)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    encrypted_content_b64 = await file.read()

    # Créer le répertoire s'il n'existe pas
    Path('test').mkdir(parents=True, exist_ok=True)

    # Chemin complet du fichier
    file_path = os.path.join('test', file.filename)

    # Écrire le contenu du fichier dans le répertoire
    with open(file_path, "wb") as f:
        f.write(encrypted_content_b64)

    return True