import unittest
from unittest.mock import patch, MagicMock
from utils import some_utility_function, another_utility_function

class TestUtils(unittest.TestCase):

    @patch('utils.some_utility_function')
    def test_some_utility_function(self, mock_some_utility_function):
        # Arrange
        mock_some_utility_function.return_value = 'expected result'
        
        # Act
        result = some_utility_function('input')

        # Assert
        self.assertEqual(result, 'expected result')
        mock_some_utility_function.assert_called_once_with('input')

    @patch('utils.another_utility_function')
    def test_another_utility_function(self, mock_another_utility_function):
        # Arrange
        mock_another_utility_function.return_value = 42
        
        # Act
        result = another_utility_function(10, 32)

        # Assert
        self.assertEqual(result, 42)
        mock_another_utility_function.assert_called_once_with(10, 32)

    def test_some_utility_function_integration(self):
        # Arrange
        input_data = 'integration input'
        
        # Act
        result = some_utility_function(input_data)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    def test_another_utility_function_integration(self):
        # Arrange
        input_data1 = 5
        input_data2 = 15
        
        # Act
        result = another_utility_function(input_data1, input_data2)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)

if __name__ == '__main__':
    unittest.main()