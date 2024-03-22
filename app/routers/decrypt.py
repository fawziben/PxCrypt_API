from fastapi import FastAPI, File, UploadFile, APIRouter, Depends, HTTPException, Response
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from .. import oauth2, models
from ..database import get_db
from sqlalchemy.orm import Session
from base64 import b64decode

router = APIRouter()

@router.post('/decrypt')
async def upload_file(file: UploadFile = File(...), current_user = Depends(oauth2.get_current_user)):
    try:
        # Lire le contenu du fichier (données chiffrées en base64)
        encrypted_content_b64 = await file.read()

        # Décoder les données chiffrées
        encrypted_content = b64decode(encrypted_content_b64)

        # Extraire l'IV des données chiffrées
        iv = encrypted_content[:16]

        # Extraire le contenu chiffré
        encrypted_data = encrypted_content[16:]

        # Récupérer la clé privée de l'utilisateur depuis la base de données
        private_key_str = current_user.private_key
        private_key_hex = bytes.fromhex(private_key_str[2:])  # Ignorer le préfixe '\x'

        # Initialiser le déchiffreur AES avec la clé et le mode CBC
        cipher = Cipher(algorithms.AES(private_key_hex), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Déchiffrer le contenu
        decrypted_content = decryptor.update(encrypted_data) + decryptor.finalize()

        # Enregistrer le fichier déchiffré sur le serveur
        with open(file.filename + ".dec", "wb") as f:
            f.write(decrypted_content)

        return Response(content=decrypted_content, media_type='application/octet-stream')

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=str(e))
