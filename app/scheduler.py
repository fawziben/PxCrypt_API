from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from .database import engine
from . import models
import os
from pathlib import Path

# Créez une session de base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def delete_expired_files():
    db = SessionLocal()  # Créez une nouvelle session
    try:
        now = datetime.utcnow()
        users = db.query(models.User).all()

        for user in users:
            # Assurez-vous que time_residency est en minutes
            retention_period = timedelta(minutes=user.time_residency)
            expiration_date = now - retention_period

            expired_files = db.query(models.Ufile).filter(
                models.Ufile.id_owner == user.id,
                models.Ufile.upload_at < expiration_date
            ).all()

            for file in expired_files:
                file_path = os.path.join(user.email, file.name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                db.delete(file)

        
        db.commit()
        print(f"Checked and deleted expired files for all users at {now}.")
    except Exception as e:
        print(f"Error while deleting expired files: {e}")
        db.rollback()
    finally:
        db.close()  # Assurez-vous de fermer la session

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_expired_files, 'interval', minutes=2, id='delete_expired_files', replace_existing=True)
    scheduler.start()
    print("Scheduler started, job will run every 2 minutes.")
