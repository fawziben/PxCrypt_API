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
    prefix="/groups",
    tags=['Groups']
)

@router.get('/', status_code=status.HTTP_200_OK)
def get_groups_by_user(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    groups = db.query(models.Group).filter(models.Group.id_owner == current_user.id).all()
    if not groups:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No sharing lists")

    result = []
    for group in groups:
        user_groups = db.query(models.User, models.User_Group).join(models.User_Group, models.User.id == models.User_Group.id_user).filter(models.User_Group.id_group == group.id).all()
        group_data = {
            "id": group.id,
            "title": group.title,
            "description": group.description,
            "users": [
                {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "user_group": user_group.id
                }
                for user, user_group in user_groups
            ]
        }
        result.append(group_data)

    return result

@router.get('/admin', status_code=status.HTTP_200_OK)
def get_groups_by_user(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_admin)):
    groups = db.query(models.Admin_Group).filter(models.Admin_Group.id_admin == current_user.id).all()
    if not groups:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No sharing lists")

    result = []
    for group in groups:
        user_groups = db.query(models.User, models.Admin_User_Group).join(models.Admin_User_Group, models.User.id == models.Admin_User_Group.id_user).filter(models.Admin_User_Group.id_group == group.id).all()
        group_data = {
            "id": group.id,
            "title": group.title,
            "description": group.description,
            "users": [
                {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "user_group": user_group.id
                }
                for user, user_group in user_groups
            ]
        }
        result.append(group_data)

    return result


@router.delete('/user_group/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user_from_group(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    try:
        user_query = db.query(models.User_Group).filter(models.User_Group.id == id)
        user = user_query.first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist or does not belong to the group")
        
        user_query.delete()
        db.commit()
        
        return {}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete('/admin/user_group/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user_from_group(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_admin)):
    try:
        user_query = db.query(models.Admin_User_Group).filter(models.Admin_User_Group.id == id)
        user = user_query.first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist or does not belong to the group")
        
        user_query.delete()
        db.commit()
        
        return {}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put('/update/title/{group_id}', status_code=status.HTTP_200_OK)
def update_group_title(group_id: int, group_title: schemas.GroupTitleUpdate, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    try:
        group = db.query(models.Group).filter(models.Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        group.title = group_title.title
        db.commit()
        return {"message": "Group title updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.put('/admin/update/title/{group_id}', status_code=status.HTTP_200_OK)
def update_group_title(group_id: int, group_title: schemas.GroupTitleUpdate, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_admin)):
    try:
        group = db.query(models.Admin_Group).filter(models.Admin_Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        group.title = group_title.title
        db.commit()
        return {"message": "Group title updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.put('/update/description/{group_id}', status_code=status.HTTP_200_OK)
def update_group_desc(group_id: int, group_description: schemas.GroupDescriptionUpdate, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    try:
        group = db.query(models.Group).filter(models.Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        group.description = group_description.description
        db.commit()
        return {"message": "Group title updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.put('/admin/update/description/{group_id}', status_code=status.HTTP_200_OK)
def update_group_desc(group_id: int, group_description: schemas.GroupDescriptionUpdate, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_admin)):
    try:
        group = db.query(models.Admin_Group).filter(models.Admin_Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        group.description = group_description.description
        db.commit()
        return {"message": "Group title updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.post('/create', status_code=status.HTTP_200_OK)
def add_group(group : schemas.GroupInfo,db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    try:
        existing_group = db.query(models.Group).filter(
        models.Group.title == group.title,
        models.Group.description == group.description,
        ).first()        
        
        if existing_group:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        
        n_group = {
            "id_owner" : current_user.id,
            "title" : group.title,
            "description" : group.description
        }
        new_group = models.Group(**n_group)
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        print(new_group.id)
        return {"id" : new_group.id}
    except HTTPException as e:
        print(f"HTTPException: {e.status_code} - {e.detail}")
        raise e
    
@router.post('/admin/create', status_code=status.HTTP_200_OK)
def add_group(group : schemas.GroupInfo,db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_admin)):
    try:
        existing_group = db.query(models.Group).filter(
        models.Admin_Group.title == group.title,
        models.Admin_Group.description == group.description,
        ).first()        
        
        if existing_group:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        
        n_group = {
            "id_admin" : current_user.id,
            "title" : group.title,
            "description" : group.description
        }
        new_group = models.Admin_Group(**n_group)
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        print(new_group.id)
        return {"id" : new_group.id}
    except HTTPException as e:
        print(f"HTTPException: {e.status_code} - {e.detail}")
        raise e



@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    try:
        # Supprimer d'abord les enregistrements dans la table sfiles
        db.query(models.User_Group).filter(models.User_Group.id_group == id).delete()

        # Ensuite, supprimer l'enregistrement dans la table ufiles
        group_query = db.query(models.Group).filter(models.Group.id == id)
        group = group_query.first()
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This group does not exist")
        
        group_query.delete()
        db.commit()

        return {}
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.delete("/admin/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_admin)):
    try:
        # Supprimer d'abord les enregistrements dans la table sfiles
        db.query(models.Admin_User_Group).filter(models.Admin_User_Group.id_group == id).delete()

        # Ensuite, supprimer l'enregistrement dans la table ufiles
        group_query = db.query(models.Admin_Group).filter(models.Admin_Group.id == id)
        group = group_query.first()
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This group does not exist")
        
        group_query.delete()
        db.commit()

        return {}
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.post('/usersadd/{id}', status_code=status.HTTP_200_OK)
def add_users_to_group(id: int, users: list[int], db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    try:
        existing_group = db.query(models.Group).filter(
            models.Group.id == id,
        ).first()

        if existing_group is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This group does not exist")
        
        new_user_ids = []  # Liste pour stocker les nouveaux identifiants d'utilisateur de groupe

        for user in users:
            new_user = models.User_Group(id_user=user, id_group=id)
            db.add(new_user)
            db.commit()
            new_user_ids.append({'id' : new_user.id, 'id_user' : user})  # Ajouter l'ID du nouvel utilisateur de groupe à la liste
            print("User added successfully")
        print (new_user_ids[0])
        return new_user_ids  # Retourner la liste des nouveaux identifiants d'utilisateur de groupe
    except HTTPException as e:
        print(f"HTTPException: {e.status_code} - {e.detail}")
        raise e
    
@router.post('/admin/usersadd/{id}', status_code=status.HTTP_200_OK)
def add_users_to_group(id: int, users: list[int], db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_admin)):
    try:
        existing_group = db.query(models.Admin_Group).filter(
            models.Admin_Group.id == id,
        ).first()

        if existing_group is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This group does not exist")
        
        new_user_ids = []  # Liste pour stocker les nouveaux identifiants d'utilisateur de groupe

        for user in users:
            new_user = models.Admin_User_Group(id_user=user, id_group=id)
            db.add(new_user)
            db.commit()
            new_user_ids.append({'id' : new_user.id, 'id_user' : user})  # Ajouter l'ID du nouvel utilisateur de groupe à la liste
            print("User added successfully")
        print (new_user_ids[0])
        return new_user_ids  # Retourner la liste des nouveaux identifiants d'utilisateur de groupe
    except HTTPException as e:
        print(f"HTTPException: {e.status_code} - {e.detail}")
        raise e

@router.get('/details', status_code=status.HTTP_200_OK)
def get_groups_by_user(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    groups = db.query(models.Group).filter(models.Group.id_owner == current_user.id).all()
    if not groups:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No sharing lists")

    result = []
    for group in groups:
        user_groups = db.query(models.User, models.User_Group).join(models.User_Group, models.User.id == models.User_Group.id_user).filter(models.User_Group.id_group == group.id).all()


    return result
