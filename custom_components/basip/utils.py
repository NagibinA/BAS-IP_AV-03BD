import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class PasswordManager:
    """Менеджер для безопасной работы с паролями"""
    
    @staticmethod
    def hash_md5(password):
        """MD5 хеширование пароля для API"""
        return hashlib.md5(password.encode()).hexdigest()
    
    @staticmethod
    def hash_sha256(password):
        """SHA256 хеширование для хранения"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def encrypt_password(password, salt=None):
        """Шифрование пароля для хранения"""
        if salt is None:
            salt = os.urandom(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        f = Fernet(key)
        encrypted = f.encrypt(password.encode())
        
        return {
            "encrypted": encrypted,
            "salt": salt
        }
    
    @staticmethod
    def decrypt_password(encrypted, salt):
        """Расшифровка пароля"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"master_key"))  # В реальном коде используйте мастер-ключ
        f = Fernet(key)
        return f.decrypt(encrypted).decode()
