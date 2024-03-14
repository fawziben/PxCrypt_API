from fastapi import HTTPException, Depends, status
from jose import JWTError, jwt
from datetime import timedelta, datetime
from . import schemas
from . import database, models
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token (data : dict) : 
    to_encode = data.copy()
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp" : expires})

    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

def verify_access_token(token : str, credentials_exception) :
    try : 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("user_id")
        if not id : 
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError : 
        raise credentials_exception
    
    return token_data
    

def get_current_user(token: str = Depends (oauth2_scheme), db : Session = Depends(database.get_db)) : 
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="""Could not validate the credentials""", 
                                          headers={"WWW:Authenticate" : "beare"})
    
    token_data = verify_access_token(token, credentials_exception)
    current_user = db.query(models.User).filter(models.User.id == token_data.id).first()
    return current_user
    
