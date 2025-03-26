import unittest
from html import escape
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/sanitize', methods=['POST'])
def sanitize_input():
    data = request.json
    sanitized_data = {key: escape(value) for key, value in data.items()}
    return jsonify(sanitized_data)

class XSSAttackTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_xss_attack(self):
        malicious_input = {
            "username": "<script>alert('XSS')</script>",
            "comment": "<img src='x' onerror='alert(1)'>"
        }
        expected_output = {
            "username": "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;",
            "comment": "&lt;img src=&#x27;x&#x27; onerror=&#x27;alert(1)&#x27;&gt;"
        }
        response = self.app.post('/sanitize', json=malicious_input)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_output)

    def test_empty_input(self):
        response = self.app.post('/sanitize', json={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {})

    def test_non_string_input(self):
        non_string_input = {
            "number": 123,
            "boolean": True,
            "null": None
        }
        response = self.app.post('/sanitize', json=non_string_input)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {
            "number": "123",
            "boolean": "True",
            "null": "None"
        })

if __name__ == '__main__':
    unittest.main()