from passlib.context import CryptContext
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def hash_pwd(pwd : str) : 
    return pwd_context.hash(pwd)

def verify_pwd(plain_pwd : str, hash_pwd : str) : 
    return pwd_context.verify(plain_pwd,hash_pwd)

def generate_aes_key(password):
    # Générer un sel aléatoire sécurisé
    salt = secrets.token_bytes(16)  # Utilise 16 octets pour un sel sécurisé
    # Définir le nombre d'itérations pour le dérivateur de clé
    iterations = 100000

    # Générer la clé à partir du mot de passe et du sel en utilisant PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # Longueur de la clé en octets (256 bits pour AES 256)
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    key = kdf.derive(b'password_1234')  # Remplacez 'password_1234' par votre mot de passe

    return key.hex() # Renvoie la clé et le sel sous forme hexadécimale