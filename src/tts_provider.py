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

import asyncio
from typing import cast

import aiohttp

from .config import config
from .constants import (
    OLLAMA_DEFAULT_ENDPOINT,
    TTS_PROVIDER_TIMEOUT_SEC,
)
from .logger import logger
from .models import TTSModels, TTSProviders
from .ollama_client import OllamaClient


class TTSProvider:
    async def async_get_tts_response(
        self,
        input: str,
        model: TTSModels,
        provider: TTSProviders,
        voice: str,
        strip_html: bool,
        note_id: int = -1,
    ) -> bytes:
        # Try local Ollama first if configured
        if config.ollama_endpoint or provider == "ollama":
            try:
                endpoint = config.ollama_endpoint or OLLAMA_DEFAULT_ENDPOINT
                ollama_client = OllamaClient(endpoint=endpoint)
                logger.debug(f"Attempting Ollama TTS with model {model} at {endpoint}")
                # Ollama's generate endpoint for TTS
                response = await ollama_client.async_get_chat_response(
                    prompt=f"Convert to speech: {input}",
                    model=cast("str", model),
                    temperature=1.0,
                )
                return response.encode() if isinstance(response, str) else response
            except Exception as e:
                logger.debug(f"Ollama TTS failed: {e}")
                # Fall through to other providers

        # Try OpenAI if provider is openai
        if provider == "openai":
            if not config.openai_api_key:
                raise RuntimeError(
                    "OpenAI TTS requires an API key. Please configure your OpenAI API key "
                    "or use local Ollama for text-to-speech."
                )

            logger.debug(f"Using OpenAI TTS with model {model} and voice {voice}")
            return await self._call_openai_tts(input, model, voice, strip_html)

        # For other providers, inform user
        raise RuntimeError(
            f"TTS provider '{provider}' requires server backend which is no longer available. "
            f"Options: Use local Ollama or configure your OpenAI API key for TTS. "
            f"Support for {provider} requires credentials configuration."
        )

    async def _call_openai_tts(
        self, input_text: str, model: TTSModels, voice: str, strip_html: bool
    ) -> bytes:
        """Call OpenAI TTS API with user-provided API key"""
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    "https://api.openai.com/v1/audio/speech",
                    headers={"Authorization": f"Bearer {config.openai_api_key}"},
                    json={
                        "model": model,
                        "input": input_text,
                        "voice": voice,
                    },
                    timeout=aiohttp.ClientTimeout(total=TTS_PROVIDER_TIMEOUT_SEC),
                ) as response,
            ):
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(
                        f"OpenAI TTS error: {response.status} - {error_text}"
                    )

                return await response.read()

        except asyncio.TimeoutError:
            raise RuntimeError(
                f"OpenAI TTS request timed out after {TTS_PROVIDER_TIMEOUT_SEC}s"
            ) from None


tts_provider = TTSProvider()
