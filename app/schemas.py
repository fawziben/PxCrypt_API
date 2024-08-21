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
    time_residency : int
    storage : int


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

class UpdateStorage(BaseModel):
    storage: int

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
    total_uploaded_size : int

class TimeResidencyUpdate(BaseModel):
    time_residency: int

class UserUpdate(BaseModel):
    firstName: str = None
    lastName: str = None
    email: EmailStr = None
    phoneNumber: str = None
    time_residency: int = None
    password : str = None

class UserStorageResponse(BaseModel):
    name: str
    storage_used: float 

class FileExtensionCountResponse(BaseModel):
    extension: str
    count: int

class PasswordRotationUpdate(BaseModel):
    value : Optional[int] 


class AddExtensionSchema(BaseModel):
    ext : str 

class AddDomainSchema(BaseModel):
    domain: str

class ExtensionResponse(BaseModel):
    id: int
    extension: str

class DomainResponse(BaseModel):
    id: int
    domain: str

class AdminParametersResponse(BaseModel):
    pwd_rotation: str
    login_attempt: str
    extensions: list[ExtensionResponse]
    domains: list[DomainResponse]