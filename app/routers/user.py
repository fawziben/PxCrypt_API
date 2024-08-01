from fastapi import Response, status, HTTPException, Depends,APIRouter
from .. import models,schemas,utils,oauth2
from ..database import get_db
from sqlalchemy.orm import Session
import shutil
import os

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.get('/', status_code=status.HTTP_200_OK, response_model=list[schemas.GetUsersResponse])
def get_users(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)): 
    users = db.query(models.User).filter(models.User.id != current_user.id).all()
    if not users: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    return users

@router.get('/admin', status_code=status.HTTP_200_OK, response_model=list[schemas.GetUsersResponse])
def get_users(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_admin)): 
    users = db.query(models.User).filter(models.User.id != current_user.id).all()
    if not users: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    return users

@router.get('/admin', status_code=status.HTTP_200_OK, response_model=list[schemas.GetUsersResponse])
def get_users(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)): 
    users = db.query(models.User).all()
    if not users: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    
    print(users[0].first_name)
    return users

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserPostResponse)
def create_user(user : schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(models.User).filter(
        models.User.email == user.email,
        models.User.phone_number == user.phone_number
        ).first()        
        
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        
        user.private_key= utils.generate_aes_key(user.password)
        user.password = utils.hash_pwd(user.password)
        new_user = models.User(**(user.model_dump()))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except HTTPException as e:
        print(f"HTTPException: {e.status_code} - {e.detail}")
        raise e

@router.get('/{id}',response_model=schemas.UserGetResponse)
def get_user(id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)) : 
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user : 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post with this index does not exist")

    return user

@router.get('/current/',status_code=status.HTTP_200_OK, response_model=schemas.CurrentUserGetResponse)
def get_current_user(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)) : 
    return current_user

@router.put('/current/name/', status_code=status.HTTP_200_OK, response_model=schemas.CurrentUserGetResponse)
def update_user_name(user_update: schemas.UserUpdateName, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    print(user_update.name)
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.first_name = user_update.name

    db.commit()
    db.refresh(user)

    return user

@router.put('/current/TFA/', status_code=status.HTTP_200_OK, response_model=schemas.CurrentUserGetResponse)
def update_TFA_state(user_update: schemas.UserUpdateName, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    print(user_update.name)
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    
    # Vérifier si l'utilisateur existe et si l'ancien mot de passe est correct
    if not user or not utils.verify_pwd(user_update.name, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid credentials'
        )
    
    user.TFA = not user.TFA

    db.commit()
    db.refresh(user)

    return user

@router.put('/current/lastname/', status_code=status.HTTP_200_OK, response_model=schemas.CurrentUserGetResponse)
def update_user_name(user_update: schemas.UserUpdateName, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    print(user_update.name)
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.last_name = user_update.name

    db.commit()
    db.refresh(user)

    return user


@router.put('/current/email/', status_code=status.HTTP_200_OK, response_model=schemas.CurrentUserGetResponse)
def update_user_name(user_update: schemas.UserUpdateEmail, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.email = user_update.email

    db.commit()
    db.refresh(user)

    return user



@router.put('/{id}',response_model=schemas.UserGetResponse)
def update_user(id : int , user : schemas.UserCreate, db: Session = Depends(get_db)) : 
    user.password = utils.hash_pwd(user.password)
    update_query = db.query(models.User).filter(models.User.id == id)
    updated_user = update_query.first()
    if not updated_user : 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post with this index does not exist")
    
    update_query.update(user.model_dump())
    db.commit()
    return update_query.first()


@router.put('/block/{id}',status_code=status.HTTP_200_OK)
def update_user(id : int , db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_admin)) : 
    user= db.query(models.User).filter(models.User.id == id).first()
    if not user : 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User with this index does not exist")
    
    user.state = not user.state
    db.commit()
    db.refresh(user)
    return {}


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_admin)):
    # Vérifiez si l'utilisateur existe
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Supprimer les références dans les autres tables
    db.query(models.Admin_User_Group).filter(models.Admin_User_Group.id_user== id).delete()

    # Supprimer les fichiers de l'utilisateur et le répertoire associé
    user_files_directory = os.path.join(user.email)
    if os.path.exists(user_files_directory):
        shutil.rmtree(user_files_directory)

    # Supprimer les entrées associées dans les tables ufiles et sfiles
    db.query(models.Ufile).filter(models.Ufile.id_owner == id).delete()

    # Supprimer l'utilisateur
    db.delete(user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)