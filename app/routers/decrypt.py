from fastapi import FastAPI, File, UploadFile, APIRouter, Depends, HTTPException, Response
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from .. import oauth2, models, utils
from ..database import get_db
from sqlalchemy.orm import Session
from base64 import b64decode
from cryptography.hazmat.primitives import padding
import mimetypes
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post('/decrypt')
async def upload_file(file: UploadFile = File(...), current_user = Depends(oauth2.get_current_user)):
    try:
        # Read the content of the file (encrypted data in base64)
        encrypted_content_b64 = await file.read()
        with open(file.filename + ".TEST", "wb") as f:
            f.write(encrypted_content_b64)
        # Decode the encrypted data
        encrypted_content = b64decode(encrypted_content_b64)

        # Extract the IV from the encrypted data
        iv = encrypted_content[:16]

        # Extract the encrypted content
        encrypted_data = encrypted_content[16:]

        # Retrieve the user's private key from the database
        private_key_str = current_user.private_key
        private_key_hex = bytes.fromhex(private_key_str[2:])  # Ignore the '\x' prefix

        # Initialize the AES decryptor with the key and CBC mode
        cipher = Cipher(algorithms.AES(private_key_hex), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the content
        decrypted_content = decryptor.update(encrypted_data) + decryptor.finalize()

        # Remove the PKCS7 padding
        unpadder = padding.PKCS7(128).unpadder()
        unpadded_content = unpadder.update(decrypted_content) + unpadder.finalize()
        print (utils.convert_size(len(encrypted_content_b64)))

        return Response(content=unpadded_content, media_type='application/octet-stream')

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=str(e))




@router.post('/view')
async def view_file_locally(file: UploadFile = File(...), current_user = Depends(oauth2.get_current_user)):
    try:
        # Read the content of the file (encrypted data in base64)
        encrypted_content_b64 = await file.read()

        # Decode the encrypted data
        encrypted_content = b64decode(encrypted_content_b64)

        # Extract the IV from the encrypted data
        iv = encrypted_content[:16]

        # Extract the encrypted content
        encrypted_data = encrypted_content[16:]

        # Retrieve the user's private key from the database
        private_key_str = current_user.private_key
        private_key_hex = bytes.fromhex(private_key_str[2:])  # Ignore the '\x' prefix

        # Initialize the AES decryptor with the key and CBC mode
        cipher = Cipher(algorithms.AES(private_key_hex), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the content
        decrypted_content = decryptor.update(encrypted_data) + decryptor.finalize()

        # Remove the PKCS7 padding
        unpadder = padding.PKCS7(128).unpadder()
        unpadded_content = unpadder.update(decrypted_content) + unpadder.finalize()

        # Determine the file extension
        ext = utils.get_true_extension(file.filename)
        print(ext)
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.txt': 'text/plain',
        }
        media_type = mime_types.get(ext, 'application/octet-stream')

        return Response(content=unpadded_content, media_type=media_type)

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=str(e))