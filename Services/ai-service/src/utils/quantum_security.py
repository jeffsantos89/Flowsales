import numpy as np

class QuantumSecurity:
    """ Segurança baseada em computação quântica (QKD) """

    @staticmethod
    def generate_quantum_key(length=128):
        return np.random.randint(2, size=length)

quantum_security = QuantumSecurity()
class QuantumSecurity:
    """ Segurança baseada em computação quântica (QKD) """

    @staticmethod
    def generate_quantum_key(length=128):
        if length <= 0:
            raise ValueError("Key length must be a positive integer")
        return np.random.randint(2, size=length)

    @staticmethod
    def encrypt_message(message, key):
        if len(message) != len(key):
            raise ValueError("Message and key must be of the same length")
        encrypted_message = ''.join(str(int(m) ^ int(k)) for m, k in zip(message, key))
        return encrypted_message

    @staticmethod
    def decrypt_message(encrypted_message, key):
        if len(encrypted_message) != len(key):
            raise ValueError("Encrypted message and key must be of the same length")
        decrypted_message = ''.join(str(int(em) ^ int(k)) for em, k in zip(encrypted_message, key))
        return decrypted_message

quantum_security = QuantumSecurity()

# Example usage
key = quantum_security.generate_quantum_key(128)
message = '10101010101010101010101010101010'  # Example binary message
encrypted_message = quantum_security.encrypt_message(message, key)
decrypted_message = quantum_security.decrypt_message(encrypted_message, key)

print(f"Original Message: {message}")
print(f"Encrypted Message: {encrypted_message}")
print(f"Decrypted Message: {decrypted_message}")