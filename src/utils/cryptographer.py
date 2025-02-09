
from cryptography.fernet import Fernet



class Cryptographer:
    def __init__(self, key: bytes | str):
        self.fernet = Fernet(key=key)

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, hash_: str) -> str:
        return self.fernet.decrypt(hash_.encode()).decode()
