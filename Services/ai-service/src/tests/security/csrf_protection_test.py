import unittest
from flask import Flask, session, request
from flask_wtf.csrf import CSRFProtect, generate_csrf

class TestCSRFProtection(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'supersecretkey'
        self.app.config['WTF_CSRF_ENABLED'] = True
        self.csrf = CSRFProtect(self.app)

        @self.app.route('/form', methods=['GET', 'POST'])
        def form():
            if request.method == 'POST':
                return 'Form submitted'
            return 'Form page'

        self.client = self.app.test_client()

    def test_csrf_token_in_form(self):
        with self.app.test_request_context():
            response = self.client.get('/form')
            self.assertEqual(response.status_code, 200)
            self.assertIn('csrf_token', response.get_data(as_text=True))

    def test_csrf_protection_on_post(self):
        with self.app.test_request_context():
            response = self.client.post('/form', data={})
            self.assertEqual(response.status_code, 400)  # CSRF token missing

            csrf_token = generate_csrf()
            response = self.client.post('/form', data={'csrf_token': csrf_token})
            self.assertEqual(response.status_code, 200)

    def test_csrf_token_in_session(self):
        with self.app.test_request_context():
            self.client.get('/form')
            self.assertIn('csrf_token', session)

    def test_invalid_csrf_token(self):
        with self.app.test_request_context():
            response = self.client.post('/form', data={'csrf_token': 'invalid_token'})
            self.assertEqual(response.status_code, 400)

    def test_csrf_token_regeneration(self):
        with self.app.test_request_context():
            self.client.get('/form')
            old_token = session['csrf_token']
            self.client.get('/form')
            new_token = session['csrf_token']
            self.assertNotEqual(old_token, new_token)

if __name__ == '__main__':
    unittest.main()