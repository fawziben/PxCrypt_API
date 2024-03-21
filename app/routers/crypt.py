from fastapi import FastAPI, File, UploadFile, APIRouter, Depends, HTTPException, Response
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from .. import oauth2, models
from ..database import get_db
from sqlalchemy.orm import Session
import binascii  # Utilisé pour convertir une chaîne hexadécimale en octets

router = APIRouter()

@router.post("/encrypt")
async def upload_file(file: UploadFile = File(...), current_user = Depends(oauth2.get_current_user)):
    try:
        # Lire le contenu du fichier
        file_content = await file.read()
        print("File content:", file_content)

        # Récupérer la clé privée de l'utilisateur sous forme d'une chaîne d'échappement Python depuis la base de données
        private_key_str = current_user.private_key

        # Convertir la chaîne d'échappement Python en une séquence d'octets hexadécimaux
        private_key_hex = bytes.fromhex(private_key_str[2:])  # Ignorer le préfixe '\x'

        # Vérifier la longueur de la clé privée
        print("Length of private key:", len(private_key_hex))

        # Initialiser le chiffrement AES avec la clé et le mode CBC
        cipher = Cipher(algorithms.AES(private_key_hex), modes.CBC(os.urandom(16)), backend=default_backend())
        encryptor = cipher.encryptor()

        # Ajouter des octets de bourrage pour que la taille du fichier soit un multiple de 16
        padded_content = file_content + b"\0" * (16 - (len(file_content) % 16))

        # Chiffrer le contenu
        encrypted_content = encryptor.update(padded_content) + encryptor.finalize()

        # Enregistrer le fichier crypté sur le serveur
        with open(file.filename + ".enc", "wb") as f:
            f.write(encrypted_content)

        print("File encrypted successfully")
        return Response(content=encrypted_content, media_type='application/octet-stream')
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=str(e))
