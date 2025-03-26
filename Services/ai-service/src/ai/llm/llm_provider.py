# src/ai/llm/llm_provider.py

from abc import ABC, abstractmethod
import logging
import openai
from openai import OpenAIError
from typing import List, Dict, Any, Optional
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dataclasses import dataclass
from enum import Enum

# Configure logging with a custom format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Supported model types"""
    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"
    GPT4_32K = "gpt-4-32k"

@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    temperature: float
    max_tokens: int
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    top_p: float = 1.0

class OpenAIConfig:
    """OpenAI specific configuration"""
    DEFAULT_MODEL = ModelType.GPT4.value
    DEFAULT_CONFIG = LLMConfig(
        temperature=0.7,
        max_tokens=512
    )
    MAX_RETRIES = 3
    BASE_WAIT = 1
    MAX_WAIT = 10
    TIMEOUT = 30.0

class LLMResponse:
    """Structured response from LLM"""
    def __init__(self, content: str, model: str, usage: Dict[str, int]):
        self.content = content
        self.model = model
        self.usage = usage

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    @abstractmethod
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        config: Optional[LLMConfig] = None
    ) -> LLMResponse:
        """Generate a response based on prompt and context"""
        pass

    @abstractmethod
    async def validate_api_key(self) -> bool:
        """Validate the API key"""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLM provider"""
    def __init__(
        self,
        api_key: str,
        model: str = OpenAIConfig.DEFAULT_MODEL,
        config: Optional[LLMConfig] = None
    ):
        if not api_key:
            raise ValueError("OpenAI API key is required")

        self.api_key = api_key
        self.model = model
        self.config = config or OpenAIConfig.DEFAULT_CONFIG
        openai.api_key = api_key

        logger.info(f"[LLM] OpenAIProvider initialized with model {self.model}")

    @retry(
        stop=stop_after_attempt(OpenAIConfig.MAX_RETRIES),
        wait=wait_exponential(multiplier=OpenAIConfig.BASE_WAIT, max=OpenAIConfig.MAX_WAIT),
        retry=retry_if_exception_type((OpenAIError, asyncio.TimeoutError)),
        reraise=True
    )
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        config: Optional[LLMConfig] = None
    ) -> LLMResponse:
        """Generate a response using OpenAI's API"""
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        try:
            messages = self._prepare_messages(context, prompt)
            config = config or self.config

            async with asyncio.timeout(OpenAIConfig.TIMEOUT):
                response = await asyncio.to_thread(
                    openai.ChatCompletion.create,
                    model=self.model,
                    messages=messages,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    presence_penalty=config.presence_penalty,
                    frequency_penalty=config.frequency_penalty,
                    top_p=config.top_p
                )

            return self._process_response(response)

        except asyncio.TimeoutError:
            logger.error("[LLM] Request timed out")
            raise
        except OpenAIError as e:
            logger.error(f"[LLM] OpenAI API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[LLM] Unexpected error: {str(e)}")
            raise

    async def validate_api_key(self) -> bool:
        """Validate the OpenAI API key"""
        try:
            await self.generate_response("test", max_tokens=1)
            return True
        except OpenAIError:
            return False

    def _prepare_messages(
        self, 
        context: Optional[str], 
        prompt: str
    ) -> List[Dict[str, str]]:
        """Prepare messages for the API call"""
        messages = []
        if context:
            messages.append({
                "role": "system",
                "content": f"Context: {context}"
            })
        messages.append({
            "role": "user",
            "content": prompt
        })
        return messages

    def _process_response(self, response: Any) -> LLMResponse:
        """Process and validate the API response"""
        try:
            return LLMResponse(
                content=response.choices[0].message['content'].strip(),
                model=response.model,
                usage=response.usage
            )
        except (KeyError, IndexError, AttributeError) as e:
            logger.error(f"[LLM] Error processing response: {str(e)}")
            raise ValueError("Invalid response format from OpenAI API")
