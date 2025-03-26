import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, request, jsonify
from time import time

# Assuming the DOS protection is implemented in a middleware
class DOSProtectionMiddleware:
    def __init__(self, app, limit=100, window=60):
        self.app = app
        self.limit = limit
        self.window = window
        self.requests = {}

    def __call__(self, environ, start_response):
        client_ip = environ.get('REMOTE_ADDR')
        current_time = time()

        if client_ip not in self.requests:
            self.requests[client_ip] = []

        self.requests[client_ip] = [timestamp for timestamp in self.requests[client_ip] if current_time - timestamp < self.window]

        if len(self.requests[client_ip]) >= self.limit:
            res = jsonify({"error": "Too many requests"}), 429
            return res(environ, start_response)

        self.requests[client_ip].append(current_time)
        return self.app(environ, start_response)

class TestDOSProtection(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.wsgi_app = DOSProtectionMiddleware(self.app.wsgi_app)
        
        @self.app.route('/test')
        def test_route():
            return jsonify({"message": "Success"})

        self.client = self.app.test_client()

    @patch('time.time', MagicMock(side_effect=[i for i in range(200)]))
    def test_dos_protection(self):
        for _ in range(100):
            response = self.client.get('/test')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"message": "Success"})

        response = self.client.get('/test')
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.json, {"error": "Too many requests"})

    @patch('time.time', MagicMock(side_effect=[i for i in range(60)]))
    def test_dos_protection_reset(self):
        for _ in range(100):
            response = self.client.get('/test')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {"message": "Success"})

        response = self.client.get('/test')
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.json, {"error": "Too many requests"})

        # Simulate waiting for the window to reset
        response = self.client.get('/test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Success"})

if __name__ == '__main__':
    unittest.main()