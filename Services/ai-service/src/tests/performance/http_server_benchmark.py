import time
import multiprocessing
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Hello, world!')

def run_server(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

def benchmark_server(url, num_requests):
    start_time = time.time()
    for _ in range(num_requests):
        response = requests.get(url)
        if response.status_code != 200:
            print(f'Error: Received status code {response.status_code}')
    end_time = time.time()
    duration = end_time - start_time
    print(f'Total time for {num_requests} requests: {duration:.2f} seconds')
    print(f'Average time per request: {duration / num_requests:.2f} seconds')

if __name__ == '__main__':
    port = 8000
    num_requests = 1000
    url = f'http://localhost:{port}'

    server_process = multiprocessing.Process(target=run_server, args=(HTTPServer, SimpleHTTPRequestHandler, port))
    server_process.start()

    time.sleep(1)  # Give the server a second to start

    try:
        benchmark_server(url, num_requests)
    finally:
        server_process.terminate()
        server_process.join()
        print('Server has been terminated.')