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
    email : EmailStr
    phone_number : str
    created_at : datetime
    img_src : Optional[str] = None
    state : bool 


class UserGetResponse (UserPostResponse) :
    password : str

class CurrentUserGetResponse (BaseModel) :
    first_name : str
    last_name : str
    email : EmailStr
    phone_number : str
    img_src : Optional[str] = None
    TFA : bool


class UserLogin(BaseModel): 
    email : EmailStr
    password : str

class AdminLogin(BaseModel): 
    username : str
    password : str

class GetUFilesResponse (BaseModel) : 
    id : int
    upload_at : datetime
    name : str
    size : str
    algorithm : str

class GetSFilesResponse(BaseModel):
    name: str
    size: str
    algorithm: str
    email: str
    shared_at: Optional[datetime] = None

class Token(BaseModel) : 
    access_token : str
    token_type : str

class TokenData (BaseModel) : 
    id : Optional [int] = None

class ShareRecipient(BaseModel):
    id: int
    download: bool
    message: str

class GroupTitleUpdate(BaseModel):
    title: str

class GroupDescriptionUpdate(BaseModel):
    description: str

class GroupInfo(BaseModel):
    title : str
    description: str

class UserUpdateName(BaseModel):
    name: str

class UserUpdateTFA(BaseModel):
    TFA: bool


class UserUpdateEmail(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    old_password: str
    new_password: str

class GetUFilesStatsResponse (BaseModel) : 
    name : str

class UserVerify (BaseModel) : 
    email : EmailStr
    code : str

class FileCountsResponse(BaseModel):
    user_files_count: int
    received_files_count: int
    shared_files_count: int

class TimeResidencyUpdate(BaseModel):
    time_residency: int