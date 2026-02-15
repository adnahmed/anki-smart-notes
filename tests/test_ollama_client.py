"""
Copyright (C) 2024 Michael Piazza

This file is part of Smart Notes.

Smart Notes is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Smart Notes is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Smart Notes.  If not, see <https://www.gnu.org/licenses/>.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.ollama_client import OllamaClient


@pytest.mark.asyncio
async def test_ollama_client_successful_response():
    """Test that OllamaClient correctly parses a successful response"""
    client = OllamaClient(endpoint="http://localhost:11434")

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "model": "llama3.2",
            "message": {"role": "assistant", "content": "Hello! How can I help you?"},
        }
    )
    mock_response.raise_for_status = MagicMock()

    with patch("aiohttp.ClientSession") as mock_session:
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response

        result = await client.async_get_chat_response(
            prompt="Hello", model="llama3.2", temperature=1.0
        )

        assert result == "Hello! How can I help you?"


@pytest.mark.asyncio
async def test_ollama_client_connection_error():
    """Test that OllamaClient handles connection errors properly"""
    client = OllamaClient(endpoint="http://localhost:11434")

    with patch("aiohttp.ClientSession") as mock_session:
        mock_session.return_value.__aenter__.return_value.post.side_effect = Exception(
            "Connection refused"
        )

        with pytest.raises(Exception, match="Max retries exceeded"):
            await client.async_get_chat_response(
                prompt="Hello", model="llama3.2", temperature=1.0
            )


def test_ollama_client_initialization():
    """Test that OllamaClient initializes with correct endpoint"""
    client = OllamaClient(endpoint="http://custom:8080")
    assert client.endpoint == "http://custom:8080"

    # Test default endpoint
    from src.constants import OLLAMA_DEFAULT_ENDPOINT

    default_client = OllamaClient()
    assert default_client.endpoint == OLLAMA_DEFAULT_ENDPOINT


@pytest.mark.asyncio
async def test_ollama_client_model_list():
    """Test that OllamaClient parses model list from /api/tags"""
    client = OllamaClient(endpoint="http://localhost:11434")

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "models": [
                {"name": "qwen2.5:7b-instruct-q6_K"},
                {"name": "llama3.2"},
            ]
        }
    )
    mock_response.raise_for_status = MagicMock()

    with patch("aiohttp.ClientSession") as mock_session:
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response

        result = await client.async_get_models()

        assert result == ["qwen2.5:7b-instruct-q6_K", "llama3.2"]
