import unittest
import requests
from requests.auth import HTTPBasicAuth

class PenetrationTest(unittest.TestCase):

    BASE_URL = "http://localhost:8000"
    ENDPOINTS = [
        "/api/v1/resource1",
        "/api/v1/resource2",
        "/api/v1/resource3"
    ]
    AUTH = HTTPBasicAuth('user', 'pass')

    def test_sql_injection(self):
        payload = "' OR '1'='1"
        for endpoint in self.ENDPOINTS:
            response = requests.get(f"{self.BASE_URL}{endpoint}?query={payload}", auth=self.AUTH)
            self.assertNotIn("error", response.text.lower(), f"SQL Injection vulnerability found at {endpoint}")

    def test_xss(self):
        payload = "<script>alert('XSS')</script>"
        for endpoint in self.ENDPOINTS:
            response = requests.post(f"{self.BASE_URL}{endpoint}", data={"input": payload}, auth=self.AUTH)
            self.assertNotIn(payload, response.text, f"XSS vulnerability found at {endpoint}")

    def test_csrf(self):
        headers = {"Referer": "http://malicious-site.com"}
        for endpoint in self.ENDPOINTS:
            response = requests.post(f"{self.BASE_URL}{endpoint}", headers=headers, auth=self.AUTH)
            self.assertNotEqual(response.status_code, 200, f"CSRF vulnerability found at {endpoint}")

    def test_brute_force(self):
        for i in range(1000):
            response = requests.get(f"{self.BASE_URL}/login", auth=HTTPBasicAuth('user', f'wrongpass{i}'))
            self.assertNotEqual(response.status_code, 200, "Brute force vulnerability found")

    def test_sensitive_data_exposure(self):
        response = requests.get(f"{self.BASE_URL}/api/v1/sensitive-data", auth=self.AUTH)
        self.assertNotIn("password", response.text.lower(), "Sensitive data exposure vulnerability found")

if __name__ == "__main__":
    unittest.main()