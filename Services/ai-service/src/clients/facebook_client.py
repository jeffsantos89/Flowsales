import httpx

class FacebookClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def send_message(self, recipient_id: str, message: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/messages", json={
                "recipient": {"id": recipient_id},
                "message": {"text": message}
            })
            response.raise_for_status()
            return response.json()

    async def get_user_profile(self, user_id: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/users/{user_id}")
            response.raise_for_status()
            return response.json()
            def __init__(self, base_url: str, access_token: str):
                self.base_url = base_url
                self.access_token = access_token
                self.client = httpx.AsyncClient(timeout=30.0)

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                await self.client.aclose()

            async def _make_request(self, method: str, endpoint: str, **kwargs):
                url = f"{self.base_url}/{endpoint}"
                kwargs['params'] = kwargs.get('params', {})
                kwargs['params']['access_token'] = self.access_token
                
                try:
                    response = await self.client.request(method, url, **kwargs)
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPError as e:
                    raise FacebookAPIError(f"Facebook API error: {str(e)}")
                except Exception as e:
                    raise FacebookClientError(f"Unexpected error: {str(e)}")

            async def send_message(self, recipient_id: str, message: str):
                return await self._make_request(
                    'POST',
                    'messages',
                    json={
                        "recipient": {"id": recipient_id},
                        "message": {"text": message}
                    }
                )

            async def get_user_profile(self, user_id: str):
                return await self._make_request('GET', f'users/{user_id}')

        class FacebookAPIError(Exception):
            pass

        class FacebookClientError(Exception):
            pass