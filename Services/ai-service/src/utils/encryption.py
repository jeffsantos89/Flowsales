import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

class EncryptionService:
    def __init__(self, key: str):
        self.key = hashlib.sha256(key.encode()).digest()

    def pad(self, data: bytes) -> bytes:
        padding_length = AES.block_size - len(data) % AES.block_size
        padding = bytes([padding_length] * padding_length)
        return data + padding

    def unpad(self, data: bytes) -> bytes:
        padding_length = data[-1]
        return data[:-padding_length]

    def encrypt(self, raw_data: str) -> str:
        raw_data_bytes = self.pad(raw_data.encode())
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(raw_data_bytes)
        return base64.b64encode(iv + encrypted_data).decode('utf-8')

    def decrypt(self, encrypted_data: str) -> str:
        encrypted_data_bytes = base64.b64decode(encrypted_data)
        iv = encrypted_data_bytes[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(encrypted_data_bytes[AES.block_size:])
        return self.unpad(decrypted_data).decode('utf-8')

# Example usage:
# key = 'your-secure-key'
# encryption_service = EncryptionService(key)
# encrypted = encryption_service.encrypt('Sensitive data')
# decrypted = encryption_service.decrypt(encrypted)
# print(f'Encrypted: {encrypted}')
# print(f'Decrypted: {decrypted}')