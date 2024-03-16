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
