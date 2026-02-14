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

from typing import cast

from .api_client import api
from .config import config
from .constants import (
    CHAT_CLIENT_TIMEOUT_SEC,
    DEFAULT_TEMPERATURE,
    OLLAMA_DEFAULT_ENDPOINT,
)
from .logger import logger
from .models import ChatModels, ChatProviders, OllamaModels
from .ollama_client import OllamaClient


class ChatProvider:
    async def async_get_chat_response(
        self,
        prompt: str,
        model: ChatModels,
        provider: ChatProviders,
        note_id: int,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> str:
        # Route to local Ollama if provider is ollama
        if provider == "ollama":
            endpoint = config.ollama_endpoint or OLLAMA_DEFAULT_ENDPOINT
            ollama_client = OllamaClient(endpoint=endpoint)

            logger.debug(
                f"Using Ollama provider with model {model} at endpoint {endpoint}"
            )

            msg = await ollama_client.async_get_chat_response(
                prompt=prompt,
                model=cast(OllamaModels, model),
                temperature=temperature,
            )

            return msg

        # Otherwise, use the cloud API server
        response = await api.get_api_response(
            path="chat",
            args={
                "provider": provider,
                "model": model,
                "message": prompt,
                "temperature": temperature,
            },
            note_id=note_id,
            timeout_sec=CHAT_CLIENT_TIMEOUT_SEC,
        )

        resp = await response.json()
        if not len(resp["messages"]):
            logger.debug(f"Empty response from chat provider {provider}")
            return ""

        msg = cast(str, resp["messages"][0])

        logger.debug(
            f"Response for prompt [{prompt}] temperature [{temperature}] model [{model}]: [{msg}]"
        )

        return msg


chat_provider = ChatProvider()
