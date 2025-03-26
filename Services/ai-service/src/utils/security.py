import hashlib
import bcrypt
import base64
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

class Security:
    def __init__(self, secret_key=None):
        """
        Initialize the Security class with a secret key.
        If no secret key is provided, it will use the one from the environment variable or generate a new one.
        """
        if secret_key:
            self.secret_key = secret_key
        else:
            self.secret_key = os.getenv("SECRET_KEY")
            if not self.secret_key:
                self.secret_key = Fernet.generate_key()
                print("Warning: No SECRET_KEY found in environment. A new key has been generated.")

        self.cipher = Fernet(self.secret_key)

    def hash_password(self, password):
        """
        Hash a password using bcrypt.
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)

    def check_password(self, password, hashed_password):
        """
        Check a password against a hashed password.
        """
        try:
            return bcrypt.checkpw(password.encode(), hashed_password)
        except ValueError:
            return False

    def encrypt(self, data):
        """
        Encrypt data using Fernet symmetric encryption.
        """
        try:
            return self.cipher.encrypt(data.encode())
        except Exception as e:
            raise ValueError(f"Encryption failed: {e}")

    def decrypt(self, encrypted_data):
        """
        Decrypt data using Fernet symmetric encryption.
        """
        try:
            return self.cipher.decrypt(encrypted_data).decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

# Example usage
if __name__ == "__main__":
    security = Security()

    password = "my_secure_password"
    hashed_password = security.hash_password(password)
    print(f"Hashed password: {hashed_password}")

    is_valid = security.check_password(password, hashed_password)
    print(f"Password is valid: {is_valid}")

    data = "Sensitive data"
    encrypted_data = security.encrypt(data)
    print(f"Encrypted data: {encrypted_data}")

    decrypted_data = security.decrypt(encrypted_data)
    print(f"Decrypted data: {decrypted_data}")
