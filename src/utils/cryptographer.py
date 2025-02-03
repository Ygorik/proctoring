import os

from cryptography.fernet import Fernet

from src.config import settings


class Cryptographer:
    def __init__(self, key: bytes = settings.CRYPTO_KEY):
        self.fernet = Fernet(key=key)

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, hash_: str) -> str:
        return self.fernet.decrypt(hash_.encode()).decode()
