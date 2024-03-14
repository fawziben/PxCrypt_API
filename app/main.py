from fastapi import Response, status, HTTPException, Depends, APIRouter, FastAPI
from time import time
import psycopg2
from psycopg2.extras import RealDictCursor
from . import database, models
from sqlalchemy.orm import Session
from .routers import user, auth

models.Base.metadata.create_all(bind=database.engine)


app = FastAPI()


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


@app.get('/')
def get_users (db : Session = Depends(database.get_db)) : 
    users = db.query(models.User).all()
    return {"data" : users}



