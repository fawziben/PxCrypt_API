from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from .database import engine
from . import models
import os
from pytz import utc

# Créez une session de base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def delete_expired_files():
    db = SessionLocal()  # Créez une nouvelle session
    try:
        now = datetime.utcnow().replace(tzinfo=utc)  # Heure actuelle en UTC

        users = db.query(models.User).all()

        for user in users:
            retention_period = timedelta(days=user.time_residency)
            expiration_date = now - retention_period

            expired_files = db.query(models.Ufile).filter(
                models.Ufile.id_owner == user.id,
                models.Ufile.upload_at < expiration_date
            ).all()

            expired_files_list = []
            for file in expired_files:
                if file.upload_at.tzinfo is None:
                    upload_at_utc = file.upload_at.replace(tzinfo=utc)
                else:
                    upload_at_utc = file.upload_at.astimezone(utc)
                
                if upload_at_utc < expiration_date:
                    expired_files_list.append(file)

            for file in expired_files_list:
                file_path = os.path.join(user.email, file.name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                db.delete(file)

        db.commit()
    except Exception as e:
        print(f"Error while deleting expired files: {e}")
        db.rollback()
    finally:
        db.close()  # Assurez-vous de fermer la session

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_expired_files, 'interval', days=1, id='delete_expired_files', replace_existing=True)
    scheduler.start()
    print("Scheduler started, job will run every 2 minutes.")
