import unittest
from unittest.mock import patch, MagicMock
from security.waf_security import WAFSecurity

class TestWAFSecurity(unittest.TestCase):

    def setUp(self):
        self.waf_security = WAFSecurity()

    @patch('security.waf_security.requests.post')
    def test_block_ip(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.waf_security.block_ip('192.168.1.1')
        self.assertTrue(result)
        mock_post.assert_called_once_with('http://waf/api/block', json={'ip': '192.168.1.1'})

    @patch('security.waf_security.requests.post')
    def test_block_ip_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = self.waf_security.block_ip('192.168.1.1')
        self.assertFalse(result)
        mock_post.assert_called_once_with('http://waf/api/block', json={'ip': '192.168.1.1'})

    @patch('security.waf_security.requests.post')
    def test_unblock_ip(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.waf_security.unblock_ip('192.168.1.1')
        self.assertTrue(result)
        mock_post.assert_called_once_with('http://waf/api/unblock', json={'ip': '192.168.1.1'})

    @patch('security.waf_security.requests.post')
    def test_unblock_ip_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = self.waf_security.unblock_ip('192.168.1.1')
        self.assertFalse(result)
        mock_post.assert_called_once_with('http://waf/api/unblock', json={'ip': '192.168.1.1'})

    @patch('security.waf_security.requests.get')
    def test_check_ip_status(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'blocked'}
        mock_get.return_value = mock_response

        status = self.waf_security.check_ip_status('192.168.1.1')
        self.assertEqual(status, 'blocked')
        mock_get.assert_called_once_with('http://waf/api/status', params={'ip': '192.168.1.1'})

    @patch('security.waf_security.requests.get')
    def test_check_ip_status_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        status = self.waf_security.check_ip_status('192.168.1.1')
        self.assertIsNone(status)
        mock_get.assert_called_once_with('http://waf/api/status', params={'ip': '192.168.1.1'})

if __name__ == '__main__':
    unittest.main()