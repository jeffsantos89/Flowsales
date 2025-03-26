import unittest
import jwt
import datetime
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = 'your_secret_key'
ALGORITHM = 'HS256'

def generate_token(payload, secret=SECRET_KEY, algorithm=ALGORITHM, expiration_minutes=30):
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=expiration_minutes)
    return jwt.encode(payload, secret, algorithm=algorithm)

def decode_token(token, secret=SECRET_KEY, algorithm=ALGORITHM):
    try:
        return jwt.decode(token, secret, algorithms=[algorithm])
    except ExpiredSignatureError:
        raise ValueError("Token has expired")
    except InvalidTokenError:
        raise ValueError("Invalid token")

class TestJWTToken(unittest.TestCase):

    def setUp(self):
        self.payload = {'user_id': 123}
        self.secret = SECRET_KEY
        self.algorithm = ALGORITHM

    def test_generate_token(self):
        token = generate_token(self.payload, self.secret, self.algorithm)
        self.assertIsInstance(token, str)

    def test_decode_token(self):
        token = generate_token(self.payload, self.secret, self.algorithm)
        decoded_payload = decode_token(token, self.secret, self.algorithm)
        self.assertEqual(decoded_payload['user_id'], self.payload['user_id'])

    def test_token_expiration(self):
        token = generate_token(self.payload, self.secret, self.algorithm, expiration_minutes=1)
        with self.assertRaises(ValueError) as context:
            # Simulate token expiration
            datetime.datetime.utcnow = lambda: datetime.datetime.utcnow() + datetime.timedelta(minutes=2)
            decode_token(token, self.secret, self.algorithm)
        self.assertEqual(str(context.exception), "Token has expired")

    def test_invalid_token(self):
        with self.assertRaises(ValueError) as context:
            decode_token("invalid_token", self.secret, self.algorithm)
        self.assertEqual(str(context.exception), "Invalid token")

if __name__ == '__main__':
    unittest.main()