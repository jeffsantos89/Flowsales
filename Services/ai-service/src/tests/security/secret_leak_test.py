import unittest
import os
from dotenv import load_dotenv
import re

class SecretLeakTest(unittest.TestCase):

    def setUp(self):
        load_dotenv()
        self.env_vars = os.environ

    def test_no_secrets_in_codebase(self):
        secret_patterns = [
            re.compile(r'AKIA[0-9A-Z]{16}'),  # AWS Access Key ID
            re.compile(r'(?i)aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40}'),  # AWS Secret Access Key
            re.compile(r'(?i)password\s*=\s*.*'),  # Generic password pattern
            re.compile(r'(?i)secret\s*=\s*.*'),  # Generic secret pattern
            re.compile(r'(?i)token\s*=\s*.*'),  # Generic token pattern
        ]

        for root, _, files in os.walk(os.path.dirname(__file__)):
            for file in files:
                if file.endswith('.py'):
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        for pattern in secret_patterns:
                            self.assertIsNone(pattern.search(content), f'Secret found in {file}')

    def test_no_secrets_in_env_vars(self):
        secret_patterns = [
            re.compile(r'AKIA[0-9A-Z]{16}'),  # AWS Access Key ID
            re.compile(r'(?i)aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40}'),  # AWS Secret Access Key
            re.compile(r'(?i)password\s*=\s*.*'),  # Generic password pattern
            re.compile(r'(?i)secret\s*=\s*.*'),  # Generic secret pattern
            re.compile(r'(?i)token\s*=\s*.*'),  # Generic token pattern
        ]

        for key, value in self.env_vars.items():
            for pattern in secret_patterns:
                self.assertIsNone(pattern.search(value), f'Secret found in environment variable {key}')

if __name__ == '__main__':
    unittest.main()