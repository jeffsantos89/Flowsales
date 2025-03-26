import unittest
from unittest.mock import patch, MagicMock
from src.marketplace import Marketplace

class TestMarketplace(unittest.TestCase):

    def setUp(self):
        self.marketplace = Marketplace()

    @patch('src.marketplace.requests.get')
    def test_get_product_details_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 1,
            'name': 'Product 1',
            'price': 100
        }
        mock_get.return_value = mock_response

        product_details = self.marketplace.get_product_details(1)
        self.assertEqual(product_details['id'], 1)
        self.assertEqual(product_details['name'], 'Product 1')
        self.assertEqual(product_details['price'], 100)

    @patch('src.marketplace.requests.get')
    def test_get_product_details_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        product_details = self.marketplace.get_product_details(999)
        self.assertIsNone(product_details)

    @patch('src.marketplace.requests.post')
    def test_create_product_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': 2,
            'name': 'Product 2',
            'price': 200
        }
        mock_post.return_value = mock_response

        new_product = {
            'name': 'Product 2',
            'price': 200
        }
        created_product = self.marketplace.create_product(new_product)
        self.assertEqual(created_product['id'], 2)
        self.assertEqual(created_product['name'], 'Product 2')
        self.assertEqual(created_product['price'], 200)

    @patch('src.marketplace.requests.post')
    def test_create_product_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        new_product = {
            'name': '',
            'price': 200
        }
        created_product = self.marketplace.create_product(new_product)
        self.assertIsNone(created_product)

    @patch('src.marketplace.requests.delete')
    def test_delete_product_success(self, mock_delete):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        result = self.marketplace.delete_product(1)
        self.assertTrue(result)

    @patch('src.marketplace.requests.delete')
    def test_delete_product_failure(self, mock_delete):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_delete.return_value = mock_response

        result = self.marketplace.delete_product(999)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()