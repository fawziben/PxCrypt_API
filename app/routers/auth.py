from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils, oauth2
from .. import database
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter(tags=['Authentication'])

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
