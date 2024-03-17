from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, TIMESTAMP
from sqlalchemy.sql import func
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