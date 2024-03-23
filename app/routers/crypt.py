from fastapi import FastAPI, File, UploadFile, APIRouter, Depends, HTTPException, Response
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from .. import oauth2, models
from ..database import get_db
from sqlalchemy.orm import Session
import binascii  # Utilisé pour convertir une chaîne hexadécimale en octets
from cryptography.hazmat.primitives import padding
from base64 import b64encode, b64decode

router = APIRouter()

@router.post("/encrypt")
async def upload_file(file: UploadFile = File(...), current_user = Depends(oauth2.get_current_user)):
    try:
        # Lire le contenu du fichier en mode binaire
        file_content = await file.read()
        with open(file.filename + ".content", "wb") as f:
            f.write(file_content)
        # Récupérer la clé privée de l'utilisateur depuis la base de données
        private_key_str = current_user.private_key
        private_key_hex = bytes.fromhex(private_key_str[2:])  # Ignorer le préfixe '\x'

        # Générer un vecteur d'initialisation aléatoire
        iv = os.urandom(16)

        # Initialiser le chiffrement AES avec la clé et le mode CBC
        cipher = Cipher(algorithms.AES(private_key_hex), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Créer un padder PKCS7
        padder = padding.PKCS7(128).padder()

        # Ajouter le bourrage PKCS7
        padded_content = padder.update(file_content) + padder.finalize()

        # Save the padded (but not yet encrypted) content to a file
        with open(file.filename + ".padded", "wb") as f:
            f.write(padded_content)

        # Chiffrer le contenu
        encrypted_content = iv + encryptor.update(padded_content) + encryptor.finalize()

        # Enregistrer le fichier crypté sur le serveur en mode binaire
        with open(file.filename + ".enc", "wb") as f:
            f.write(encrypted_content)

        # Convertir les données chiffrées en base64 pour la transmission
        encrypted_content_b64 = b64encode(encrypted_content)

        return Response(content=encrypted_content_b64, media_type='application/octet-stream')

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=str(e))
