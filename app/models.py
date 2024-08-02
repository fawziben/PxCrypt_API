from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text

DEFAULT_STORAGE_BITS = 100 * 1024 * 1024 * 8


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
    img_src = Column(String, nullable=True)  # Assurez-vous que cette colonne existe
    verification_code = Column(String,nullable=True)
    code_expiry = Column(DateTime, nullable= True)
    TFA = Column (Boolean,nullable=False,default=True)
    state = Column (Boolean,nullable=False,default=True)
    time_residency = Column(Integer, nullable=False, default=7)  # Durée en jours
    storage = Column (Integer, nullable=False, server_default=str(DEFAULT_STORAGE_BITS))


    
class Sfile(Base):
    __tablename__ = "sfiles"

    id = Column(Integer, primary_key=True, nullable=False)
    id_receiver = Column(Integer, ForeignKey('users.id'), nullable=False)
    id_file = Column(Integer, ForeignKey('ufiles.id', ondelete="CASCADE"), nullable=False)
    shared_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    download = Column(Boolean, nullable=False)
    message = Column(String, nullable=False)

    # Relation Many-to-One avec la table Ufile
    file = relationship("Ufile", back_populates="sfiles")
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

class Group(Base) : 
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, nullable=False)
    id_owner = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)


class Admin_Group(Base) : 
    __tablename__ = "admin_groups"

    id = Column(Integer, primary_key=True, nullable=False)
    id_admin = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    time_residency = Column(Integer, nullable=False, default=7)  # Durée en jours



class User_Group (Base) : 
    __tablename__ = "user_group"

    id = Column(Integer, primary_key=True, nullable=False)
    id_user = Column(Integer, ForeignKey('users.id'), nullable=False)
    id_group = Column(Integer, ForeignKey('groups.id'), nullable=False)

    user = relationship("User", foreign_keys=[id_user])
    group = relationship("Group", foreign_keys=[id_group])

class Admin_User_Group (Base) : 
    __tablename__ = "admin_user_group"

    id = Column(Integer, primary_key=True, nullable=False)
    id_user = Column(Integer, ForeignKey('users.id'), nullable=False)
    id_group = Column(Integer, ForeignKey('admin_groups.id'), nullable=False)

    user = relationship("User", foreign_keys=[id_user])
    group = relationship("Admin_Group", foreign_keys=[id_group])


    
class Admin(Base) : 
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)

    
