from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models,schemas,utils,oauth2
from .. import database
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


router = APIRouter(tags=['Authentication'])

@router.post('/login')
# OAuth2PasswordRequestForm is build in fastapi option which is a like a dict {"username" : "sdfsdf", 
# "password" : "jksdfj"}. And to make a request we no longer use the raw section to send 
# credentials. Instead we send them via the form-data section
def login(user_credentials : OAuth2PasswordRequestForm = Depends(),db: Session = Depends(database.get_db)): 
    user = db.query(models.User).filter(user_credentials.username == models.User.email).first()
    if not user : 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid credentials')
    
    if not utils.verify_pwd (user_credentials.password, user.password) : 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid credentials')
    
    access_token = oauth2.create_access_token(data={"user_id" : user.id})
    
    return ({"access_token" : access_token, "token_type" : "bearer"})
