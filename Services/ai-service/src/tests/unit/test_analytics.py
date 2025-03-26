import unittest
from unittest.mock import patch, MagicMock
from analytics import AnalyticsService

class TestAnalyticsService(unittest.TestCase):

    def setUp(self):
        self.analytics_service = AnalyticsService()

    @patch('analytics.requests.post')
    def test_send_event_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        response = self.analytics_service.send_event('test_event', {'key': 'value'})
        self.assertTrue(response)
        mock_post.assert_called_once_with('http://analytics-service/events', json={'event': 'test_event', 'data': {'key': 'value'}})

    @patch('analytics.requests.post')
    def test_send_event_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        response = self.analytics_service.send_event('test_event', {'key': 'value'})
        self.assertFalse(response)
        mock_post.assert_called_once_with('http://analytics-service/events', json={'event': 'test_event', 'data': {'key': 'value'}})

    @patch('analytics.requests.post')
    def test_send_event_exception(self, mock_post):
        mock_post.side_effect = Exception('Network error')

        response = self.analytics_service.send_event('test_event', {'key': 'value'})
        self.assertFalse(response)
        mock_post.assert_called_once_with('http://analytics-service/events', json={'event': 'test_event', 'data': {'key': 'value'}})

    def test_validate_event_data(self):
        valid_data = {'key': 'value'}
        invalid_data = 'invalid_data'

        self.assertTrue(self.analytics_service.validate_event_data(valid_data))
        self.assertFalse(self.analytics_service.validate_event_data(invalid_data))

if __name__ == '__main__':
    unittest.main()