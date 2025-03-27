import httpx

class WhatsAppClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def send_message(self, payload: dict):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/messages", json=payload)
            response.raise_for_status()
            return response.json()

    async def get_message_status(self, message_id: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/messages/{message_id}/status")
            response.raise_for_status()
            return response.json()
            def __init__(self, base_url: str, timeout: int = 30, max_retries: int = 3):
                self.base_url = base_url
                self.timeout = timeout
                self.client = httpx.AsyncClient(
                    timeout=timeout,
                    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
                    transport=httpx.AsyncHTTPTransport(retries=max_retries)
                )

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                await self.close()

            async def close(self):
                await self.client.aclose()

            async def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
                try:
                    response = await self.client.request(
                        method,
                        f"{self.base_url}/{endpoint.lstrip('/')}",
                        **kwargs
                    )
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPError as e:
                    logging.error(f"WhatsApp API error: {str(e)}")
                    raise
                except Exception as e:
                    logging.error(f"Unexpected error: {str(e)}")
                    raise

            async def send_message(self, payload: dict) -> dict:
                return await self._make_request("POST", "messages", json=payload)

            async def get_message_status(self, message_id: str) -> dict:
                return await self._make_request("GET", f"messages/{message_id}/status")