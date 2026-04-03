"""
OpenRouter API Client - INTENTIONALLY VULNERABLE
Zero security measures - direct passthrough to LLM
"""
import httpx
import os
from typing import AsyncIterator, Optional
import json


class OpenRouterClient:
    """
    Async client for OpenRouter API.
    WARNING: This client has NO security measures and will pass any input directly to the LLM.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key. If None, uses OPENROUTER_API_KEY from environment.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.model = os.getenv("VICTIM_MODEL", "meta-llama/llama-3.3-70b-instruct")
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def chat(self, message: str, temperature: float = 0.7) -> str:
        """
        Send a message to the LLM and get a response.
        
        NO INPUT VALIDATION - messages are passed directly to the LLM.
        NO RATE LIMITING - unlimited requests allowed.
        NO AUTHENTICATION CHECKS - no user verification.
        
        Args:
            message: User message (unfiltered, no validation)
            temperature: LLM temperature parameter
            
        Returns:
            LLM response as string
            
        Raises:
            Exception: On API errors
        """
        # INTENTIONALLY NO INPUT VALIDATION OR SANITIZATION
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": message,  # DIRECT PASSTHROUGH - NO FILTERING
                        }
                    ],
                    "temperature": temperature,
                },
                timeout=30.0,
            )
            
            if response.status_code != 200:
                raise Exception(
                    f"OpenRouter API error: {response.status_code} - {response.text}"
                )
            
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def stream_chat(
        self, message: str, temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """
        Stream a message to the LLM and yield chunks.
        
        NO INPUT VALIDATION - messages are passed directly to the LLM.
        
        Args:
            message: User message (unfiltered)
            temperature: LLM temperature parameter
            
        Yields:
            Response chunks as strings
        """
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": message,  # DIRECT PASSTHROUGH
                        }
                    ],
                    "temperature": temperature,
                    "stream": True,
                },
                timeout=30.0,
            ) as stream:
                async for line in stream.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            pass
