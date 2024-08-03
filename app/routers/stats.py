from fastapi import Response, status, HTTPException, Depends,APIRouter
from .. import models,schemas,utils,oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func  # Importer func de SQLAlchemy pour les fonctions d'agrégation
from sqlalchemy import cast, Integer


router = APIRouter(
    prefix="/stats",
    tags=['Statistics']
)
@router.get('/ufiles/{id}', status_code=status.HTTP_200_OK, response_model=dict)
def get_user_files_count(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)): 
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user with this index found")

    nbfiles = db.query(models.Ufile).filter(models.Ufile.id_owner == id).count()
    return {'count': nbfiles}


@router.get('/rfiles/{id}', status_code=status.HTTP_200_OK, response_model=dict)
def get_user_files_count(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)): 
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user with this index found")

    nbfiles = db.query(models.Sfile).filter(models.Sfile.id_receiver == id).count()
    return {'count': nbfiles}


@router.get('/sfiles/{id}', status_code=status.HTTP_200_OK)
def get_file_count(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user with this index found")

    file_count = db.query(models.Sfile) \
        .join(models.Ufile, models.Sfile.id_file == models.Ufile.id) \
        .filter(models.Ufile.id_owner == id) \
        .count()

    return {'count': file_count}





@router.get('/file-counts/{id}', status_code=status.HTTP_200_OK, response_model=schemas.FileCountsResponse)
def get_file_counts(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # Vérifiez si l'utilisateur existe
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user with this index found")

    # Comptez les fichiers de l'utilisateur
    user_files_count = db.query(models.Ufile).filter(models.Ufile.id_owner == id).count()

    # Comptez les fichiers reçus par l'utilisateur
    received_files_count = db.query(models.Sfile).filter(models.Sfile.id_receiver == id).count()

    # Comptez les fichiers partagés par l'utilisateur
    shared_files_count = db.query(models.Sfile) \
        .join(models.Ufile, models.Sfile.id_file == models.Ufile.id) \
        .filter(models.Ufile.id_owner == id) \
        .count()

    # Calculez la taille totale des fichiers uploadés par l'utilisateur (en octets)
    total_uploaded_size = db.query(func.sum(cast(models.Ufile.size, Integer))) \
        .filter(models.Ufile.id_owner == id) \
        .scalar() or 0  # Utiliser 0 comme valeur par défaut si aucun fichier n'est trouvé

    print(total_uploaded_size)
    return {
        'user_files_count': user_files_count,
        'received_files_count': received_files_count,
        'shared_files_count': shared_files_count,
        'total_uploaded_size': total_uploaded_size  # Ajouter la taille totale des fichiers uploadés
    }




