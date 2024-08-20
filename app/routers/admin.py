from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db
from ..utils import hash_pwd

router = APIRouter(
    prefix="/admin",
    tags=['Admin']
)

@router.put('/update_user/{id}', status_code=status.HTTP_200_OK)
def update_user_name(
    id: int,
    up_user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(oauth2.get_current_admin)
):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update the fields if new values are provided
    if up_user.firstName is not None:
        user.first_name = up_user.firstName
    if up_user.lastName is not None:
        user.last_name = up_user.lastName
    if up_user.email is not None:
        user.email = up_user.email
    if up_user.phoneNumber is not None:
        user.phone_number = up_user.phoneNumber
    if up_user.time_residency is not None:
        user.time_residency = up_user.time_residency
    if up_user.password is not None:
        user.password = hash_pwd(up_user.password)

    db.commit()
    db.refresh(user)

    return user
