from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def hash_pwd(pwd : str) : 
    return pwd_context.hash(pwd)

def verify_pwd(plain_pwd : str, hash_pwd : str) : 
    return pwd_context.verify(plain_pwd,hash_pwd)