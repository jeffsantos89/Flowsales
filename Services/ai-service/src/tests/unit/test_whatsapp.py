import unittest
from unittest.mock import patch, MagicMock
from src.services.whatsapp_service import WhatsAppService

class TestWhatsAppService(unittest.TestCase):

    def setUp(self):
        self.whatsapp_service = WhatsAppService()
        self.phone_number = "+1234567890"
        self.message = "Hello, this is a test message."

    @patch('src.services.whatsapp_service.requests.post')
    def test_send_message_success(self, mock_post):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        # Act
        response = self.whatsapp_service.send_message(self.phone_number, self.message)

        # Assert
        self.assertTrue(response["status"] == "success")
        mock_post.assert_called_once_with(
            self.whatsapp_service.api_url,
            json={
                "phone_number": self.phone_number,
                "message": self.message
            },
            headers=self.whatsapp_service.headers
        )

    @patch('src.services.whatsapp_service.requests.post')
    def test_send_message_failure(self, mock_post):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"status": "failure", "error": "Invalid phone number"}
        mock_post.return_value = mock_response

        # Act
        response = self.whatsapp_service.send_message(self.phone_number, self.message)

        # Assert
        self.assertTrue(response["status"] == "failure")
        self.assertEqual(response["error"], "Invalid phone number")
        mock_post.assert_called_once_with(
            self.whatsapp_service.api_url,
            json={
                "phone_number": self.phone_number,
                "message": self.message
            },
            headers=self.whatsapp_service.headers
        )

    @patch('src.services.whatsapp_service.requests.post')
    def test_send_message_exception(self, mock_post):
        # Arrange
        mock_post.side_effect = Exception("Network error")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.whatsapp_service.send_message(self.phone_number, self.message)
        self.assertTrue("Network error" in str(context.exception))
        mock_post.assert_called_once_with(
            self.whatsapp_service.api_url,
            json={
                "phone_number": self.phone_number,
                "message": self.message
            },
            headers=self.whatsapp_service.headers
        )

if __name__ == '__main__':
    unittest.main()