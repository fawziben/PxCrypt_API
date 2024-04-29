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

router = APIRouter(
    prefix="/files",
    tags=['Files']
)

from app import models

@router.post('/share/{id}', status_code=status.HTTP_200_OK)
async def share_file(id: int, users_list: list[int], db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    try:
        for user_id in users_list:
            new_sfile = models.Sfile(id_receiver=user_id, id_file=id)
            db.add(new_sfile)
        db.commit()
        print("Files shared successfully")

    except Exception as e:
        print(f"Error while sharing files: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to share files")

    
@router.post('/upload', status_code=status.HTTP_200_OK)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    encrypted_content_b64 = await file.read()
    existing_file = db.query(models.Ufile).filter(
        models.Ufile.name == file.filename,
        ).first()        
        
    if existing_file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A file with this name has already been uploaded")    

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
    files = db.query(models.Ufile).filter(models.Ufile.id_owner == current_user.id).all()
    if not files: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No uploaded files found")
    return files


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    try:
        # Supprimer d'abord les enregistrements dans la table sfiles
        db.query(models.Sfile).filter(models.Sfile.id_file == id).delete()

        # Ensuite, supprimer l'enregistrement dans la table ufiles
        file_query = db.query(models.Ufile).filter(models.Ufile.id == id)
        file = file_query.first()
        if file is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File with this ID does not exist")
        
        file_path = os.path.join(current_user.email, file.name)
        print(file_path)
        file_query.delete()
        db.commit()

        if os.path.exists(file_path):
            os.remove(file_path)
        return {}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get('/shared', status_code=status.HTTP_200_OK,)
def get_sfiles(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    files = db.query(models.Sfile).join(models.Ufile).join(models.User).filter(models.Sfile.id_receiver == current_user.id).all()
    if not files: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No shared files found")
    # Mappez les résultats sur le modèle de réponse
    response_data = [{"date":file.file.upload_at ,"name": file.file.name, "size": file.file.size, "algorithm": file.file.algorithm, "sender": file.file.owner.email} for file in files]
    return response_data


