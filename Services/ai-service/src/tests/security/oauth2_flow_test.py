import unittest
from unittest.mock import patch, MagicMock
from oauthlib.oauth2 import WebApplicationClient
from requests import Session
from myapp.security.oauth2_flow import OAuth2Flow

class TestOAuth2Flow(unittest.TestCase):

    def setUp(self):
        self.client_id = 'test_client_id'
        self.client_secret = 'test_client_secret'
        self.authorization_url = 'https://example.com/oauth/authorize'
        self.token_url = 'https://example.com/oauth/token'
        self.redirect_uri = 'https://example.com/callback'
        self.scope = ['profile', 'email']
        self.oauth2_flow = OAuth2Flow(
            client_id=self.client_id,
            client_secret=self.client_secret,
            authorization_url=self.authorization_url,
            token_url=self.token_url,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        )
        self.session = MagicMock(spec=Session)
        self.client = WebApplicationClient(self.client_id)

    @patch('myapp.security.oauth2_flow.requests.Session', return_value=MagicMock())
    def test_get_authorization_url(self, mock_session):
        auth_url, state = self.oauth2_flow.get_authorization_url()
        self.assertIn(self.authorization_url, auth_url)
        self.assertIsNotNone(state)

    @patch('myapp.security.oauth2_flow.requests.Session', return_value=MagicMock())
    def test_fetch_token(self, mock_session):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'expires_in': 3600
        }
        mock_session.return_value.post.return_value = mock_response

        token = self.oauth2_flow.fetch_token('test_authorization_response')
        self.assertEqual(token['access_token'], 'test_access_token')
        self.assertEqual(token['refresh_token'], 'test_refresh_token')

    @patch('myapp.security.oauth2_flow.requests.Session', return_value=MagicMock())
    def test_refresh_token(self, mock_session):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'expires_in': 3600
        }
        mock_session.return_value.post.return_value = mock_response

        new_token = self.oauth2_flow.refresh_token('test_refresh_token')
        self.assertEqual(new_token['access_token'], 'new_access_token')
        self.assertEqual(new_token['refresh_token'], 'new_refresh_token')

    @patch('myapp.security.oauth2_flow.requests.Session', return_value=MagicMock())
    def test_revoke_token(self, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.return_value.post.return_value = mock_response

        response = self.oauth2_flow.revoke_token('test_access_token')
        self.assertTrue(response)

if __name__ == '__main__':
    unittest.main()