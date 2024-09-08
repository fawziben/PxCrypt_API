from datetime import datetime, timedelta
from fastapi import Response, status, HTTPException, Depends,APIRouter, UploadFile, File, Body
from .. import models,schemas,utils,oauth2
from ..database import get_db
from sqlalchemy.orm import Session
import shutil
import os
import base64

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



@router.post("/verify_email", status_code=status.HTTP_200_OK)
async def create_user(user : schemas.UserEmailVerify, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(models.User).filter(
        models.User.email == user.email,
        models.User.phone_number == user.phone_number
        ).first()        
        
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        
        param = db.query(models.Admin_Parameter).first() 

        if not param:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Erreur lors de la generation de code verification")
        
        param.verification_code = utils.generate_verification_code()
        param.code_expiry = datetime.utcnow() + timedelta(minutes=10)
        db.commit()
        db.refresh(param)
        await utils.send_email(user.email,param.verification_code)
        return {}
    except HTTPException as e:
        print(f"HTTPException: {e.status_code} - {e.detail}")
        raise e

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Retrieve the admin parameters
        param = db.query(models.Admin_Parameter).first()
        if not param:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Erreur lors de la verification du code"
            )
        
        # Check verification code and expiration
        if user.code != param.verification_code or param.code_expiry < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid or expired verification code'
            )

        # Extract domain from email
        email_domain = f"@{user.user.email.split('@')[1]}"
        print(f"Extracted email domain: {email_domain}")

        # Determine if all domains are allowed
        if param.all_domains:
            user_state = True
        else:
            # Check if the domain is allowed
            domain_exists = db.query(models.Domain).filter(models.Domain.domain == email_domain).first()
            if domain_exists:
                user_state = True
            else:
                user_state = False

        # Generate keys and hash password
        user.user.private_key = utils.generate_aes_key(user.user.password)
        user.user.password = utils.hash_pwd(user.user.password)

        # Set the user's state based on the domain check
        # user.user.state = user_state

        # Create new user in the database
        new_user = models.User(**(user.user.model_dump()))
        new_user.state = user_state
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"state": user_state}

    except HTTPException as e:
        print(f"HTTPException: {e.status_code} - {e.detail}")
        raise e
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_user(user : schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        user.user.private_key= utils.generate_aes_key(user.user.password)
        user.user.password = utils.hash_pwd(user.user.password)
        new_user = models.User(**(user.user.model_dump()))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"id" : new_user.id}
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



def add_padding(base64_string):
    missing_padding = len(base64_string) % 4
    if missing_padding:
        base64_string += '=' * (4 - missing_padding)
    return base64_string

@router.put('/current/image/', status_code=status.HTTP_200_OK, response_model=schemas.CurrentUserGetResponse)
def update_user_image(
    image_data: str = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user)
):
    if not image_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No image data provided")

    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Decode the Base64 string
    try:
        header, encoded = image_data.split(",", 1)  # Assumes the Base64 string is in a data URL format
        encoded = add_padding(encoded)  # Add padding if necessary
        image_bytes = base64.b64decode(encoded)
        print("Decoded image bytes:", len(image_bytes))
    except Exception as e:
        print("Error decoding Base64 string:", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Base64 string")

    # Determine file location
    file_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images'))
    file_location = os.path.join(file_dir, f"{current_user.id}_profile_image.png")
    file_url = f"http://127.0.0.1:8000/static/{current_user.id}_profile_image.png"
    
    try:
        os.makedirs(file_dir, exist_ok=True)  # Ensure directory exists
        with open(file_location, "wb") as buffer:
            buffer.write(image_bytes)
        print("File saved successfully at:", file_location)
    except Exception as e:
        print("Error saving file:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File save error")

    user.img_src = file_url
    db.commit()
    db.refresh(user)
    print("User image path updated in DB:", user.img_src)

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

@router.put('/admin/update/storage/{id}',status_code=status.HTTP_200_OK)
def update_user(id : int , storage: schemas.UpdateStorage,  db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_admin)) : 
    user= db.query(models.User).filter(models.User.id == id).first()
    if not user : 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User with this index does not exist")
    
    user.storage = storage.storage
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
    db.query(models.Admin_User_Group).filter(models.Admin_User_Group.id_user == id).delete()
    db.query(models.User_Group).filter(models.User_Group.id_user == id).delete()
    db.query(models.Ufile).filter(models.Ufile.id_owner == id).delete()
    db.query(models.Sfile).filter(models.Sfile.id_receiver == id).delete()  # Assurez-vous que la table et la colonne sont correctes

    # Supprimer les fichiers de l'utilisateur et le répertoire associé
    user_files_directory = os.path.join(user.email)
    if os.path.exists(user_files_directory):
        shutil.rmtree(user_files_directory)

    # Supprimer l'utilisateur
    db.delete(user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete('/delete/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db)):
    # Vérifiez si l'utilisateur existe
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Supprimer les références dans les autres tables
    db.query(models.Admin_User_Group).filter(models.Admin_User_Group.id_user == id).delete()
    db.query(models.User_Group).filter(models.User_Group.id_user == id).delete()
    db.query(models.Ufile).filter(models.Ufile.id_owner == id).delete()
    db.query(models.Sfile).filter(models.Sfile.id_receiver == id).delete()  # Assurez-vous que la table et la colonne sont correctes

    # Supprimer les fichiers de l'utilisateur et le répertoire associé
    user_files_directory = os.path.join(user.email)
    if os.path.exists(user_files_directory):
        shutil.rmtree(user_files_directory)

    # Supprimer l'utilisateur
    db.delete(user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)