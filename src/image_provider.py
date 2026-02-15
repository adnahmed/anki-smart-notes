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
    IMAGE_PROVIDER_TIMEOUT_SEC,
    MAX_RETRIES,
    OLLAMA_DEFAULT_ENDPOINT,
    RETRY_BASE_SECONDS,
)
from .logger import logger
from .models import ImageModels, ImageProviders
from .ollama_client import OllamaClient


class ImageProvider:
    async def async_get_image_response(
        self, prompt: str, model: ImageModels, provider: ImageProviders, note_id: int
    ) -> bytes:
        # Try local Ollama first if it's configured
        if config.ollama_endpoint:
            try:
                endpoint = config.ollama_endpoint or OLLAMA_DEFAULT_ENDPOINT
                ollama_client = OllamaClient(endpoint=endpoint)
                logger.debug(
                    f"Attempting Ollama image generation with model {model} at {endpoint}"
                )
                # Ollama's generate endpoint for images
                response = await ollama_client.async_get_chat_response(
                    prompt=f"Generate an image of: {prompt}",
                    model=cast("str", model),
                    temperature=1.0,
                )
                return response.encode() if isinstance(response, str) else response
            except Exception as e:
                logger.debug(f"Ollama image generation failed: {e}")
                # Fall through to other providers

        # Try Replicate if provider is replicate
        if provider == "replicate":
            # Users should configure their own Replicate API key
            replicate_api_key = config.openai_api_key  # Could store as separate key
            if not replicate_api_key:
                raise RuntimeError(
                    "Image generation provider 'replicate' requires API credentials. "
                    "Please configure your API key or use local Ollama with image models like flux."
                )

            logger.debug(
                f"Using Replicate provider with model {model} for image generation"
            )
            return await self._call_replicate(prompt, model, replicate_api_key)

        # Fallback: inform user about options
        raise RuntimeError(
            f"Image generation provider '{provider}' is not available. "
            "Options: Use local Ollama with image models (flux-schnell, etc.) or "
            "configure a Replicate API key for cloud-based generation."
        )

    async def _call_replicate(
        self, prompt: str, model: ImageModels, api_key: str, retry_count: int = 0
    ) -> bytes:
        """Call Replicate API for image generation (requires user API key)"""
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "version": self._replicate_model_to_version(model),
                        "input": {"prompt": prompt},
                    },
                    timeout=aiohttp.ClientTimeout(total=IMAGE_PROVIDER_TIMEOUT_SEC),
                ) as response,
            ):
                if response.status == 429:
                    if retry_count < MAX_RETRIES:
                        wait_time = (2**retry_count) * RETRY_BASE_SECONDS
                        logger.debug(
                            f"Replicate rate limit. Retry {retry_count}, waiting {wait_time}s"
                        )
                        await asyncio.sleep(wait_time)
                        return await self._call_replicate(
                            prompt, model, api_key, retry_count + 1
                        )
                elif response.status != 201:
                    error_text = await response.text()
                    raise RuntimeError(
                        f"Replicate API error: {response.status} - {error_text}"
                    )

                result = await response.json()
                output_url = result.get("output", [None])[0]
                if not output_url:
                    raise RuntimeError("No output from Replicate API")

                # Download the image
                async with session.get(output_url) as img_response:
                    return await img_response.read()

        except asyncio.TimeoutError:
            raise RuntimeError(
                f"Replicate image generation timed out after {IMAGE_PROVIDER_TIMEOUT_SEC}s"
            ) from None

    def _replicate_model_to_version(self, model: ImageModels) -> str:
        """Map model name to Replicate version"""
        model_map = {
            "flux-dev": "black-forest-labs/flux-dev",
            "flux-schnell": "black-forest-labs/flux-schnell",
        }
        return model_map.get(model, "black-forest-labs/flux-schnell")


image_provider = ImageProvider()
