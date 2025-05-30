from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text

DEFAULT_STORAGE_BYTES = 100 * 1024 * 1024  # 100 Mo en octets


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
    storage = Column (Integer, nullable=False, server_default=str(DEFAULT_STORAGE_BYTES))
    attempts = Column (Integer, nullable=False, default=0)


    
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
    verification_code = Column(String,nullable=True)
    code_expiry = Column(DateTime, nullable= True)

    
class Admin_Parameter(Base):
    __tablename__ = "admin_parameters"

    id = Column(Integer, primary_key=True, nullable=False)
    pwd_rotation = Column(String, nullable=True,default=3)
    login_attempt = Column(String, nullable=True,default=5)
    all_domains = Column(Boolean, default=True)  # Nouvelle colonne
    all_extensions = Column(Boolean, default=True)  # Nouvelle colonne
    verification_code = Column(String, nullable=True)  # Nouvelle colonne
    code_expiry = Column(DateTime, nullable=True)  # Changement de type vers DateTime


class Extension(Base) : 
    __tablename__ = "extensions"

    id = Column(Integer, primary_key=True, nullable=False)
    extension = Column(String, nullable=False)

class Domain(Base) : 
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, nullable=False)
    domain = Column(String, nullable=False)


class User_Notification(Base):
    __tablename__ = "user_notifications"

    id = Column(Integer, primary_key=True, nullable=False)
    id_user = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    id_notifier = Column(Integer, ForeignKey('users.id'))
    type = Column(String, nullable=True)
    unread = Column(Boolean, default=True)
    date = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    file_name = Column(String, nullable=True)  # Nouvelle colonne


    # Définir la relation avec User
    user = relationship("User", foreign_keys=[id_user])
    notifier = relationship("User", foreign_keys=[id_notifier])

class Admin_Notification(Base):
    __tablename__ = "admin_notifications"

    id = Column(Integer, primary_key=True, nullable=False)
    id_admin = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    id_notifier = Column(Integer, ForeignKey('users.id'))
    type = Column(String, nullable=True)
    unread = Column(Boolean, default=True)
    date = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    detail = Column(String, nullable=True)  # Nouvelle colonne


    # Définir la relation avec User
    admin = relationship("Admin", foreign_keys=[id_admin])
    notifier = relationship("User", foreign_keys=[id_notifier])