from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate (BaseModel) :
    first_name : str
    last_name : str
    email : EmailStr
    phone_number : int
    password : str

class UserPostResponse (BaseModel) :
    id : int
    first_name : str
    last_name : str
    email : EmailStr
    phone_number : int

class UserGetResponse (UserPostResponse) :
    password : str
