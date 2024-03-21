from fastapi import Response, status, HTTPException, Depends, APIRouter, FastAPI
from time import time
import psycopg2
from psycopg2.extras import RealDictCursor
from . import database, models
from sqlalchemy.orm import Session
from .routers import user, auth, crypt
from fastapi.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=database.engine)


app = FastAPI()

# Configurer les en-têtes CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autoriser les requêtes depuis n'importe quelle origine
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Autoriser les méthodes HTTP spécifiées
    allow_headers=["*"],  # Autoriser tous les en-têtes dans les requêtes
)


while True :
    try:
        conn = psycopg2.connect(host = 'localhost', database= 'PxCrypt_DB', password = 'admin', user = 'postgres',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('Connection established successfully')
        break
    except Exception as error : 
        print('connection failed')
        print('ERROR :', error)
        time.sleep(2)


app.include_router(user.router)
app.include_router(auth.router)
app.include_router(crypt.router)


@app.get('/')
def get_users (db : Session = Depends(database.get_db)) : 
    users = db.query(models.User).all()
    return {"data" : users}



