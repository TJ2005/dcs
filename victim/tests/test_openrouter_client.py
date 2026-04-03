"""
Unit tests for OpenRouter API client
Tests the async client without making actual API calls
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from openrouter_client import OpenRouterClient


@pytest.fixture
def mock_api_key():
    """Provide mock API key"""
    return "test-api-key-12345"


@pytest.fixture
def client(mock_api_key):
    """Create client with mock API key"""
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": mock_api_key}):
        return OpenRouterClient(api_key=mock_api_key)


class TestOpenRouterClientInitialization:
    """Test client initialization"""

    def test_init_with_api_key(self, mock_api_key):
        """Test initialization with explicit API key"""
        client = OpenRouterClient(api_key=mock_api_key)
        assert client.api_key == mock_api_key

    def test_init_from_environment(self, mock_api_key):
        """Test initialization from environment variable"""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": mock_api_key}):
            client = OpenRouterClient()
            assert client.api_key == mock_api_key

    def test_init_missing_api_key(self):
        """Test initialization fails without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                OpenRouterClient()

    def test_default_model(self, client):
        """Test default model is set correctly"""
        assert client.model == "meta-llama/llama-3.3-70b-instruct"

    def test_custom_model(self, mock_api_key):
        """Test custom model from environment"""
        with patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": mock_api_key,
                "VICTIM_MODEL": "custom-model",
            },
        ):
            client = OpenRouterClient()
            assert client.model == "custom-model"

    def test_headers_format(self, client):
        """Test headers are formatted correctly"""
        assert "Authorization" in client.headers
        assert client.headers["Authorization"].startswith("Bearer ")
        assert client.headers["Content-Type"] == "application/json"


class TestOpenRouterClientChat:
    """Test chat functionality"""

    @pytest.mark.asyncio
    async def test_chat_success(self, client):
        """Test successful chat request"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }

        with patch("openrouter_client.httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.post.return_value = mock_response
            mock_async_client.return_value = mock_instance

            response = await client.chat("Test message")
            assert response == "Test response"

    @pytest.mark.asyncio
    async def test_chat_with_temperature(self, client):
        """Test chat with custom temperature"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response"}}]
        }

        with patch("openrouter_client.httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.post.return_value = mock_response
            mock_async_client.return_value = mock_instance

            response = await client.chat("Test", temperature=0.5)
            assert response == "Response"

    @pytest.mark.asyncio
    async def test_chat_api_error(self, client):
        """Test chat handles API errors"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        with patch("openrouter_client.httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.post.return_value = mock_response
            mock_async_client.return_value = mock_instance

            with pytest.raises(Exception):
                await client.chat("Test")

    @pytest.mark.asyncio
    async def test_chat_no_input_validation(self, client):
        """Test that chat accepts any input without validation"""
        attack_messages = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "A" * 10000,  # Long message
            "null",
            "",  # Empty (will be rejected at API level)
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response"}}]
        }

        with patch("openrouter_client.httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value.post.return_value = mock_response
            mock_async_client.return_value = mock_instance

            for msg in attack_messages[:-1]:  # Skip empty string
                response = await client.chat(msg)
                assert response == "Response"


class TestOpenRouterClientStream:
    """Test streaming functionality"""

    @pytest.mark.asyncio
    async def test_stream_chat_success(self, client):
        """Test successful stream chat"""
        stream_data = [
            'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            'data: {"choices":[{"delta":{"content":" "}}]}\n',
            'data: {"choices":[{"delta":{"content":"world"}}]}\n',
            "data: [DONE]\n",
        ]

        with patch("openrouter_client.httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_stream = AsyncMock()
            mock_stream.aiter_lines = AsyncMock(return_value=iter(stream_data))
            mock_instance.__aenter__.return_value.stream.return_value.__aenter__.return_value = (
                mock_stream
            )
            mock_async_client.return_value = mock_instance

            chunks = []
            async for chunk in client.stream_chat("Test"):
                chunks.append(chunk)

            assert len(chunks) == 3
            assert "".join(chunks) == "Hello world"

    @pytest.mark.asyncio
    async def test_stream_chat_malformed_json(self, client):
        """Test stream handles malformed JSON gracefully"""
        stream_data = [
            'data: {"choices":[{"delta":{"content":"Good"}}]}\n',
            "data: {bad json\n",
            'data: {"choices":[{"delta":{"content":"Fine"}}]}\n',
            "data: [DONE]\n",
        ]

        with patch("openrouter_client.httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_stream = AsyncMock()
            mock_stream.aiter_lines = AsyncMock(return_value=iter(stream_data))
            mock_instance.__aenter__.return_value.stream.return_value.__aenter__.return_value = (
                mock_stream
            )
            mock_async_client.return_value = mock_instance

            chunks = []
            async for chunk in client.stream_chat("Test"):
                chunks.append(chunk)

            assert len(chunks) == 2
            assert "".join(chunks) == "GoodFine"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
