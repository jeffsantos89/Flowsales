import unittest
from unittest.mock import patch, MagicMock

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

class TestMathOperations(unittest.TestCase):

    def test_add(self):
        self.assertEqual(add(1, 2), 3)
        self.assertEqual(add(-1, 1), 0)
        self.assertEqual(add(-1, -1), -2)

    def test_subtract(self):
        self.assertEqual(subtract(2, 1), 1)
        self.assertEqual(subtract(-1, 1), -2)
        self.assertEqual(subtract(-1, -1), 0)

    def test_multiply(self):
        self.assertEqual(multiply(2, 3), 6)
        self.assertEqual(multiply(-1, 1), -1)
        self.assertEqual(multiply(-1, -1), 1)

    def test_divide(self):
        self.assertEqual(divide(6, 3), 2)
        self.assertEqual(divide(-1, 1), -1)
        self.assertEqual(divide(-1, -1), 1)
        with self.assertRaises(ValueError):
            divide(1, 0)

    @patch('builtins.print')
    def test_mock_print(self, mock_print):
        print("Hello, World!")
        mock_print.assert_called_with("Hello, World!")

if __name__ == '__main__':
    unittest.main()