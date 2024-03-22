from fastapi import FastAPI, File, UploadFile, APIRouter, Depends, HTTPException, Response
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from .. import oauth2, models
from ..database import get_db
from sqlalchemy.orm import Session
from base64 import b64encode

router = APIRouter()

@router.post("/encrypt")
async def upload_file(file: UploadFile = File(...), current_user = Depends(oauth2.get_current_user)):
    try:
        # Lire le contenu du fichier en mode binaire pour obtenir des octets
        file_content = await file.read()
        
        # Générer un vecteur d'initialisation aléatoire
        iv = os.urandom(16)

        # Récupérer la clé privée de l'utilisateur depuis la base de données
        private_key_str = current_user.private_key
        private_key_hex = bytes.fromhex(private_key_str[2:])  # Ignorer le préfixe '\x'

        # Initialiser le chiffrement AES avec la clé et le mode CBC
        cipher = Cipher(algorithms.AES(private_key_hex), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Chiffrer les données
        encrypted_content = encryptor.update(file_content) + encryptor.finalize()

        # Combiner l'IV et les données chiffrées
        encrypted_data = iv + encrypted_content

        # Convertir les données chiffrées en base64 pour la transmission
        encrypted_data_b64 = b64encode(encrypted_data)

        # Enregistrer les données chiffrées sur le serveur (facultatif)
        with open(file.filename + ".enc", "wb") as f:
            f.write(encrypted_data)

        return Response(content=encrypted_data_b64, media_type="application/octet-stream")

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=str(e))
