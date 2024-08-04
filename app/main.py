from fastapi import FastAPI, Depends
from time import sleep
import psycopg2
from psycopg2.extras import RealDictCursor
from . import database, models, schemas
from sqlalchemy.orm import Session
from .routers import user, auth, crypt, decrypt, files, groups, stats
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extensions import adapt, register_adapter
from .scheduler import start_scheduler  # Importer le scheduler
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=database.engine)


start_scheduler()

# Créez un adaptateur pour le type GroupTitleUpdate
def adapt_group_title_update(value):
    return adapt(value.title.encode('utf-8'))

def adapt_group_desc_update(value):
    return adapt(value.description.encode('utf-8'))

# Enregistrez l'adaptateur
register_adapter(schemas.GroupTitleUpdate, adapt_group_title_update)
register_adapter(schemas.GroupDescriptionUpdate, adapt_group_desc_update)

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/images"), name="static")

# Configurer les en-têtes CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autoriser les requêtes depuis n'importe quelle origine
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Autoriser les méthodes HTTP spécifiées
    allow_headers=["*"],  # Autoriser tous les en-têtes dans les requêtes
)

# Démarrer le scheduler en arrière-plan

while True:
    try:
        conn = psycopg2.connect(
            host='localhost', database='PxCrypt_DB', password='admin', user='postgres',
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        print('Connection established successfully')
        break
    except Exception as error:
        print('Connection failed')
        print('ERROR:', error)
        sleep(2)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(crypt.router)
app.include_router(decrypt.router)
app.include_router(files.router)
app.include_router(groups.router)
app.include_router(stats.router)

@app.get('/')
def get_users(db: Session = Depends(database.get_db)):
    users = db.query(models.User).all()
    return {"data": users}
