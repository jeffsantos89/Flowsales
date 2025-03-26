import random
import logging
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime
import asyncio
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Server:
    name: str
    host: str
    port: int
    health_check_endpoint: str = "/health"
    is_active: bool = True
    last_response_time: float = 0
    error_count: int = 0

class LoadBalancer:
    def __init__(self):
        self.servers: List[Server] = [
            Server(name="ai-node-1", host="localhost", port=8001),
            Server(name="ai-node-2", host="localhost", port=8002),
            Server(name="ai-node-3", host="localhost", port=8003),
        ]
        self.max_retries = 3
        self.error_threshold = 5
        self.health_check_interval = 30  # seconds

    async def check_server_health(self, server: Server) -> None:
        """Verifica a saúde do servidor através de uma requisição HTTP."""
        url = f"http://{server.host}:{server.port}{server.health_check_endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                start_time = datetime.now().timestamp()
                async with session.get(url, timeout=5) as response:
                    end_time = datetime.now().timestamp()
                    
                    if response.status == 200:
                        server.last_response_time = end_time - start_time
                        server.error_count = 0
                        server.is_active = True
                    else:
                        server.error_count += 1
        except Exception as e:
            logger.error(f"Health check failed for {server.name}: {str(e)}")
            server.error_count += 1
            
        if server.error_count >= self.error_threshold:
            server.is_active = False

    async def health_check_loop(self):
        """Loop contínuo de verificação de saúde dos servidores."""
        while True:
            tasks = [self.check_server_health(server) for server in self.servers]
            await asyncio.gather(*tasks)
            await asyncio.sleep(self.health_check_interval)

    def get_best_server(self) -> Server:
        """Seleciona o melhor servidor com base em disponibilidade e performance."""
        available_servers = [s for s in self.servers if s.is_active]
        
        if not available_servers:
            raise RuntimeError("No servers available")

        # Prioriza servidores com menor tempo de resposta
        return min(available_servers, key=lambda s: s.last_response_time)

    async def start(self):
        """Inicia o load balancer."""
        logger.info("Starting load balancer...")
        await self.health_check_loop()

if __name__ == "__main__":
    load_balancer = LoadBalancer()
    
    try:
        asyncio.run(load_balancer.start())
    except KeyboardInterrupt:
        logger.info("Shutting down load balancer...")
