from fastapi import Response, status, HTTPException, Depends,APIRouter
from .. import models,schemas,utils
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserPostResponse)
def create_user(user : schemas.UserCreate, db: Session = Depends(get_db)) :
    #ce type de requetes avec %s permet d'eviter les attaques par injection
    # cursor.execute("""INSERT INTO posts (title,content,is_published) VALUES (%s,%s,%s) RETURNING * """, (post.title,post.content,post.posted))
    # new_post = cursor.fetchone()
    # conn.commit()
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    user.password = utils.hash_pwd(user.password)
    new_user = models.User(**(user.model_dump()))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/{id}',response_model=schemas.UserGetResponse)
def get_user(id: int, db: Session = Depends(get_db)) : 
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
