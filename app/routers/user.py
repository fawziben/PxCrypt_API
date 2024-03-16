from fastapi import Response, status, HTTPException, Depends,APIRouter
from .. import models,schemas,utils,oauth2
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserPostResponse)
def create_user(user : schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(models.User).filter(models.User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        
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
