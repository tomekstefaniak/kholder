# Validation utilities for API inputs

def validate_label(label: str) -> str:
    if len(label) < 1 or len(label) > 128:
        raise ValueError("Label length must be between 1 and 128 characters long")
    return label
    
def validate_password(password: str) -> str:
    if len(password) < 1 or len(password) > 128:
        raise ValueError("Password must be between 1 and 128 characters long")
    return password

def validate_decrypted_key(value: str) -> str:
    if len(value) < 1 or len(value) > 4096:
        raise ValueError("Decrypted value must be between 1 and 4096 characters long")
    return value


# Cyrptographic utilities for encryption/decryption

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
import base64
import os


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(
        kdf.derive(password.encode())
    )

def encrypt(text: str, password: str) -> bytes:
    salt = os.urandom(16)
    key = derive_key(password, salt)
    fernet = Fernet(key)
    ciphertext = fernet.encrypt(text.encode())
    return salt + ciphertext

def decrypt(data: bytes, password: str) -> str:
    salt = data[:16]
    ciphertext = data[16:]
    key = derive_key(password, salt)
    fernet = Fernet(key)
    return fernet.decrypt(ciphertext).decode()
