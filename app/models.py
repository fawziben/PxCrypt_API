from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text

class User (Base) : 
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String(length=10))
    email = Column(String, unique=True, nullable=False) 
    password = Column (String,nullable=False)
    private_key = Column (String,server_default=None)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    
class Sfile(Base):
    __tablename__ = "sfiles"

    id = Column(Integer, primary_key=True, nullable=False)
    id_receiver = Column(Integer, ForeignKey('users.id'), nullable=False)
    id_file = Column(Integer, ForeignKey('ufiles.id'), nullable=False)
    shared_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # Relation Many-to-One avec la table Ufile
    file = relationship("Ufile", back_populates="sfiles")

    # Contraintes de clé étrangère
    receiver = relationship("User", foreign_keys=[id_receiver])
    file = relationship("Ufile", foreign_keys=[id_file])
    


class Ufile(Base):
    __tablename__ = "ufiles"

    id = Column(Integer, primary_key=True, nullable=False)
    id_owner = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    size = Column(String, nullable=False)
    algorithm = Column(String, nullable=False)
    upload_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # Relation One-to-Many avec la table Sfile avec cascade
    sfiles = relationship("Sfile", back_populates="file", cascade="all, delete-orphan")
    owner = relationship("User", foreign_keys=[id_owner])
