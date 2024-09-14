from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64decode
from cryptography.hazmat.primitives import padding


def decrypt_data (data,pk) : 
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
