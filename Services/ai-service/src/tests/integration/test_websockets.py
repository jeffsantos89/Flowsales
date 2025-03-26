import pytest
import asyncio
import websockets
import json
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch
from datetime import datetime

class TestWebSocketConnection:
    @pytest.fixture
    async def websocket_client(self) -> AsyncGenerator:
        """Fixture to create a websocket client connection."""
        uri = "ws://localhost:8000/ws"  # Adjust the URI according to your setup
        async with websockets.connect(uri) as websocket:
            yield websocket

    @pytest.fixture
    def mock_database(self):
        """Fixture to mock database connections."""
        with patch('src.database.Database') as mock_db:
            mock_db.return_value = AsyncMock()
            yield mock_db

    @pytest.mark.asyncio
    async def test_websocket_connection_establishment(self, websocket_client):
        """Test successful websocket connection."""
        assert websocket_client.open is True
        assert websocket_client.closed is False

    @pytest.mark.asyncio
    async def test_websocket_message_exchange(self, websocket_client):
        """Test sending and receiving messages through websocket."""
        test_message = {
            "type": "message",
            "content": "Hello, WebSocket!",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send message
        await websocket_client.send(json.dumps(test_message))
        
        # Receive response with timeout
        try:
            response = await asyncio.wait_for(
                websocket_client.recv(),
                timeout=5.0
            )
            response_data = json.loads(response)
            
            assert "type" in response_data
            assert "content" in response_data
            assert "timestamp" in response_data
        except asyncio.TimeoutError:
            pytest.fail("Websocket response timeout")

    @pytest.mark.asyncio
    async def test_websocket_error_handling(self, websocket_client):
        """Test error handling for invalid messages."""
        invalid_message = "invalid_json{}"
        
        await websocket_client.send(invalid_message)
        
        response = await websocket_client.recv()
        response_data = json.loads(response)
        
        assert response_data["type"] == "error"
        assert "message" in response_data

    @pytest.mark.asyncio
    async def test_websocket_concurrent_connections(self):
        """Test multiple concurrent websocket connections."""
        uri = "ws://localhost:8000/ws"
        num_connections = 5
        
        async def connect_and_send():
            async with websockets.connect(uri) as ws:
                message = {
                    "type": "ping",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await ws.send(json.dumps(message))
                response = await ws.recv()
                return json.loads(response)
        
        # Create multiple concurrent connections
        tasks = [connect_and_send() for _ in range(num_connections)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all connections were successful
        for response in responses:
            assert isinstance(response, dict)
            assert response["type"] == "pong"

    @pytest.mark.asyncio
    async def test_websocket_authentication(self, websocket_client):
        """Test websocket authentication process."""
        auth_message = {
            "type": "auth",
            "token": "test_token",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await websocket_client.send(json.dumps(auth_message))
        response = await websocket_client.recv()
        response_data = json.loads(response)
        
        assert response_data["type"] == "auth_response"
        assert "status" in response_data

    @pytest.mark.asyncio
    async def test_websocket_reconnection(self):
        """Test websocket reconnection capability."""
        uri = "ws://localhost:8000/ws"
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                async with websockets.connect(uri) as ws:
                    assert ws.open is True
                    break
            except websockets.exceptions.ConnectionClosed:
                if attempt == max_retries - 1:
                    pytest.fail("Failed to reconnect after maximum retries")
                await asyncio.sleep(retry_delay)

    def test_websocket_config_validation(self):
        """Test websocket configuration validation."""
        from src.config import WebSocketConfig  # Adjust import path
        
        test_config = WebSocketConfig(
            host="localhost",
            port=8000,
            path="/ws",
            max_connections=1000,
            timeout=60
        )
        
        assert test_config.host == "localhost"
        assert test_config.port == 8000
        assert test_config.path == "/ws"
        assert test_config.max_connections == 1000
        assert test_config.timeout == 60
