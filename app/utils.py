from passlib.context import CryptContext
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
import math


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
    key = kdf.derive(password.encode())  # Utilisez le mot de passe fourni pour dériver la clé

    return key


def convert_size(size_bytes):
    """
    Convertit la taille du fichier en une chaîne lisible par l'homme (B, KB, MB, GB, TB, PB)
    """
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
