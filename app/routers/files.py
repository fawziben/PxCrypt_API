from fastapi import FastAPI, File, UploadFile, APIRouter, Depends, HTTPException, Response, status
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from pathlib import Path
from .. import oauth2, models, utils, schemas
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
    ufile = {}
    encrypted_content_b64 = await file.read()

    ufile = models.Ufile(
        name=file.filename,
        id_owner = current_user.id,
        size=utils.convert_size(len(encrypted_content_b64)),
        algorithm='AES_256'
    )
    db.add(ufile)
    db.commit()
    db.refresh(ufile)
    print(ufile.size)
    # Créer le répertoire s'il n'existe pas
    Path(current_user.email).mkdir(parents=True, exist_ok=True)

    # Chemin complet du fichier
    file_path = os.path.join(current_user.email, file.filename)

    # Écrire le contenu du fichier dans le répertoire
    with open(file_path, "wb") as f:
        f.write(encrypted_content_b64)

    return True

@router.get('/uploaded', status_code=status.HTTP_200_OK,response_model=list[schemas.GetUFilesResponse])
def get_ufiles(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    files = db.query(models.Ufile).all()
    if not files: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No uploaded files found")
    return files
