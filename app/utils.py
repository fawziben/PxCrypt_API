from passlib.context import CryptContext
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
import math
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64decode, b64encode
from cryptography.hazmat.primitives import padding
import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from requests import Session

import app.models as models


def generate_verification_code():
    return secrets.token_hex(3)  # Générer un code de vérification


conf = ConnectionConfig(
    MAIL_USERNAME ="benmoumenfawzi@gmail.com",
    MAIL_PASSWORD = "sxrm ddul wqxa btae",
    MAIL_FROM = "benmoumenfawzi@gmail.com",
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)


def html(number) : 
    return f"""
<h1> Votre code d'authentification est : {number} </h1> 
"""


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

def encrypt_data(data,pk) : 
        private_key_hex = bytes.fromhex(pk[2:])  # Ignorer le préfixe '\x'

        # Générer un vecteur d'initialisation aléatoire
        iv = os.urandom(16)

        # Initialiser le chiffrement AES avec la clé et le mode CBC
        cipher = Cipher(algorithms.AES(private_key_hex), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Créer un padder PKCS7
        padder = padding.PKCS7(128).padder()

        # Ajouter le bourrage PKCS7
        padded_content = padder.update(data) + padder.finalize()

        # Chiffrer le contenu
        encrypted_content = iv + encryptor.update(padded_content) + encryptor.finalize()

        # Convertir les données chiffrées en base64 pour la transmission
        encrypted_content_b64 = b64encode(encrypted_content)

        return encrypted_content_b64

async def send_email(email,code) :    
    message = MessageSchema(
        subject="OTP",
        recipients=[email],
        body=html(code),
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

def notify_user(id_user: int, db: Session, notification_type: str, id_notifier: int,file_name:str):
    # Créer une nouvelle notification
    new_notification = models.User_Notification(
        id_user=id_user,
        id_notifier = id_notifier,
        type=notification_type,
        unread=True,  # Par défaut, la notification est non lue
        file_name = file_name
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return new_notification

def notify_admin(id_admin: int, db: Session, notification_type: str, id_notifier: int,detail:str):
    # Créer une nouvelle notification
    new_notification = models.Admin_Notification(
        id_admin=id_admin,
        id_notifier = id_notifier,
        type=notification_type,
        unread=True,  # Par défaut, la notification est non lue
        detail = detail
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return new_notification