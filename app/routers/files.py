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


@router.post('/share/{id}', status_code=status.HTTP_200_OK)
async def share_file(id: int, recipients: list[schemas.ShareRecipient], db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    try:
        myfile = db.query(models.Ufile).filter(models.Ufile.id == id).first()
        if myfile is None : 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='This file does not exist')
        
        print(recipients)
        for recipient in recipients:
            new_sfile = models.Sfile(id_receiver=recipient.id, id_file=id,download=recipient.download,message=recipient.message)
            new_notif = utils.notify_user(recipient.id,db,"share",current_user.id,myfile.name)
            db.add(new_sfile)
        db.commit()
        print("Files shared successfully")

    except Exception as e:
        print(f"Error while sharing files: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to share files")


from sqlalchemy.orm import joinedload


@router.post('/group_share/{id}', status_code=status.HTTP_200_OK)
async def share_file(
    id: int,
    recipients: list[schemas.ShareRecipient],
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    try:
        user_ids = set()
        new_files = []
        new_notifs = []

        # Récupérer les IDs des groupes d'admin présents dans recipients
        admin_group_ids = set(recipient.id for recipient in recipients if recipient.is_admin)

        for recipient in recipients:
            group_id = recipient.id
            download = recipient.download
            message = recipient.message

            # Récupérer les utilisateurs des groupes de l'utilisateur
            group_users = db.query(models.User_Group).filter(
                models.User_Group.id_group == group_id
            ).all()

            if not group_users:
                print(f"Group with id {group_id} does not exist or has no users.")
                continue

            for group_user in group_users:
                user_id = group_user.id_user
                
                # Vérifier si l'utilisateur existe dans la table users
                user_exists = db.query(models.User).filter(models.User.id == user_id).first()
                
                if user_exists:
                    if user_id not in user_ids:
                        user_ids.add(user_id)
                        print(f"User ID {user_id} exists in users table.")
                        new_sfile = models.Sfile(id_receiver=user_id, id_file=id, download=download, message=message)
                        new_notif = utils.notify_user(user_id,db,"share",current_user.id)
                        new_files.append(new_sfile)
                else:
                    print(f"User ID {user_id} does not exist in users table.")

        # Inclure les utilisateurs des groupes administratifs présents dans recipients
        for admin_group_id in admin_group_ids:
            admin_group_users = db.query(models.User, models.Admin_User_Group).join(
                models.Admin_User_Group, models.User.id == models.Admin_User_Group.id_user
            ).filter(models.Admin_User_Group.id_group == admin_group_id).all()

            for admin_user, admin_user_group in admin_group_users:
                user_id = admin_user.id

                # Vérifier si l'utilisateur existe dans la table users
                if user_id not in user_ids:
                    user_ids.add(user_id)
                    print(f"Admin User ID {user_id} exists in users table.")
                    new_sfile = models.Sfile(id_receiver=user_id, id_file=id, download=recipient.download, message=recipient.message)
                    new_notif = utils.notify_user(user_id,db,"share",current_user.id)

                    new_files.append(new_sfile)
                else:
                    print(f"Admin User ID {user_id} is already included.")

        if new_files:
            # Ajouter les nouvelles entrées dans la base de données
            db.bulk_save_objects(new_files)
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
        models.Ufile.id_owner == current_user.id
        ).first()        
        
    if existing_file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A file with this name has already been uploaded")    

    ufile = models.Ufile(
        name=file.filename,
        id_owner = current_user.id,
        size=len(encrypted_content_b64),
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


@router.delete("/uploaded/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
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
        file_query.delete()
        db.commit()

        if os.path.exists(file_path):
            os.remove(file_path)
        return {}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/shared/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    try:
        print(id)
        # Supprimer d'abord les enregistrements dans la table sfiles
        db.query(models.Sfile).filter(models.Sfile.id == id).delete()
        db.commit()

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
    response_data = [{"date":file.file.upload_at ,"name": file.file.name, "size": file.file.size, "algorithm": file.file.algorithm, "sender": file.file.owner.email, "file_id" :file.file.id, "id" : file.id} for file in files]
    return response_data

@router.get('/{id}', status_code=status.HTTP_200_OK)
def get_ufile_by_id(id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    file = db.query(models.Ufile).filter(models.Ufile.id == id).first()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This file does not exist in the database")

    # Construire le chemin complet du fichier
    if file.id_owner != current_user.id:
        user = db.query(models.User).filter(models.User.id == file.id_owner).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This file does not exist anymore")
        pk = user.private_key
        file_path = os.path.join(user.email, file.name)
    else:
        pk = current_user.private_key
        file_path = os.path.join(current_user.email, file.name)

    with open(file_path, "rb") as f:
        file_data = f.read()

    plain_data = utils.decrypt(file_data, pk)

    ext = utils.get_true_extension(file.name)
    print(ext)
    mime_types = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.txt': 'text/plain',
    }
    media_type = mime_types.get(ext, 'application/octet-stream')

    return Response(content=plain_data, media_type=media_type)

@router.get('/stats/uploaded', status_code=status.HTTP_200_OK,response_model=list[schemas.GetUFilesStatsResponse])
def get_ufiles(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    files = db.query(models.Ufile).filter(models.Ufile.id_owner == current_user.id).all()
    if not files: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No uploaded files found")
    return files