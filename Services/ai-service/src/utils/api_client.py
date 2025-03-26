import requests
from requests.adapters import HTTPAdapter, Retry
from urllib.parse import urljoin

class APIClient:
    def __init__(self, base_url, timeout=10, retries=3, backoff_factor=0.3):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(total=retries, backoff_factor=backoff_factor, status_forcelist=[502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _request(self, method, endpoint, **kwargs):
        url = urljoin(self.base_url, endpoint)
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except requests.exceptions.ConnectionError as conn_err:
            print(f'Connection error occurred: {conn_err}')
        except requests.exceptions.Timeout as timeout_err:
            print(f'Timeout error occurred: {timeout_err}')
        except requests.exceptions.RequestException as req_err:
            print(f'An error occurred: {req_err}')
        return None

    def get(self, endpoint, params=None, headers=None):
        return self._request('GET', endpoint, params=params, headers=headers)

    def post(self, endpoint, data=None, json=None, headers=None):
        return self._request('POST', endpoint, data=data, json=json, headers=headers)

    def put(self, endpoint, data=None, json=None, headers=None):
        return self._request('PUT', endpoint, data=data, json=json, headers=headers)

    def delete(self, endpoint, headers=None):
        return self._request('DELETE', endpoint, headers=headers)

# Example usage:
# client = APIClient('https://api.example.com/')
# response = client.get('/endpoint')