from passlib.context import CryptContext
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
import math
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64decode
from cryptography.hazmat.primitives import padding
import os


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

def decrypt (data,pk) : 
    # Read the content of the file (encrypted data in base64)
    encrypted_content = b64decode(data)

        # Extract the IV from the encrypted data
    iv = encrypted_content[:16]

        # Extract the encrypted content
    encrypted_data = encrypted_content[16:]

        # Retrieve the user's private key from the database
    private_key_str = pk
    private_key_hex = bytes.fromhex(private_key_str[2:])  # Ignore the '\x' prefix

        # Initialize the AES decryptor with the key and CBC mode
    cipher = Cipher(algorithms.AES(private_key_hex), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

        # Decrypt the content
    decrypted_content = decryptor.update(encrypted_data) + decryptor.finalize()

        # Remove the PKCS7 padding
    unpadder = padding.PKCS7(128).unpadder()
    unpadded_content = unpadder.update(decrypted_content) + unpadder.finalize()
    return unpadded_content

def get_true_extension(file_name):
    while '.' in file_name:
        file_name, ext = os.path.splitext(file_name)
        if ext.lower() in ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.txt']:
            return ext.lower()
    return None
