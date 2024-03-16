from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate (BaseModel) :
    first_name : str
    last_name : str
    email : EmailStr
    phone_number : str
    password : str

class UserPostResponse (BaseModel) :
    id : int
    first_name : str
    last_name : str
    email : EmailStr
    phone_number : str

class UserGetResponse (UserPostResponse) :
    password : str

class UserLogin(BaseModel): 
    email : EmailStr
    password : str


class Token(BaseModel) : 
    access_token : str
    token_type : str

class TokenData (BaseModel) : 
    id : Optional [int] = None