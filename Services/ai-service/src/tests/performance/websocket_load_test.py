import asyncio
import websockets
import time
import json
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)

class WebSocketLoadTest:
    def __init__(self, uri, message, num_clients, duration):
        self.uri = uri
        self.message = message
        self.num_clients = num_clients
        self.duration = duration
        self.executor = ThreadPoolExecutor(max_workers=num_clients)

    async def send_message(self, websocket):
        await websocket.send(json.dumps(self.message))
        response = await websocket.recv()
        logging.info(f"Received: {response}")

    async def connect_client(self):
        async with websockets.connect(self.uri) as websocket:
            start_time = time.time()
            while time.time() - start_time < self.duration:
                await self.send_message(websocket)

    async def run_test(self):
        tasks = [self.connect_client() for _ in range(self.num_clients)]
        await asyncio.gather(*tasks)

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run_test())

if __name__ == "__main__":
    uri = "ws://localhost:8000/ws"
    message = {"type": "ping"}
    num_clients = 100
    duration = 60  # seconds

    load_test = WebSocketLoadTest(uri, message, num_clients, duration)
    load_test.start()