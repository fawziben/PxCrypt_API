from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate (BaseModel) :
    first_name : str
    last_name : str
    email : EmailStr
    phone_number : str
    password : str
    private_key: Optional[str] = None

class UserPostResponse (BaseModel) :
    id : int
    first_name : str
    last_name : str
    email : EmailStr
    phone_number : str

class GetUsersResponse (BaseModel) : 
    id : int
    first_name : str
    last_name : str

class UserGetResponse (UserPostResponse) :
    password : str

class UserLogin(BaseModel): 
    email : EmailStr
    password : str

class GetUFilesResponse (BaseModel) : 
    id : int
    upload_at : datetime
    name : str
    size : str
    algorithm : str

class Token(BaseModel) : 
    access_token : str
    token_type : str

class TokenData (BaseModel) : 
    id : Optional [int] = None