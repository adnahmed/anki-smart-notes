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

import aiohttp

from .constants import (
    DEFAULT_TEMPERATURE,
    MAX_RETRIES,
    OLLAMA_DEFAULT_ENDPOINT,
    OLLAMA_TIMEOUT_SEC,
    RETRY_BASE_SECONDS,
)
from .logger import logger
from .models import OllamaModels

timeout = aiohttp.ClientTimeout(total=OLLAMA_TIMEOUT_SEC)


class OllamaClient:
    """Client for local Ollama chat API."""

    def __init__(self, endpoint: str = OLLAMA_DEFAULT_ENDPOINT):
        self.endpoint = endpoint

    async def async_get_chat_response(
        self,
        prompt: str,
        model: OllamaModels,
        temperature: float = DEFAULT_TEMPERATURE,
        retry_count: int = 0,
    ) -> str:
        """Gets a chat response from Ollama's chat API. This method can throw; the caller should handle with care."""
        endpoint = f"{self.endpoint}/api/chat"

        logger.debug(
            f"Ollama: hitting {endpoint} model: {model} retries {retry_count} for prompt: {prompt}"
        )
        try:
            async with (
                aiohttp.ClientSession(timeout=timeout) as session,
                session.post(
                    endpoint,
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                        },
                    },
                ) as response,
            ):
                if response.status == 429:
                    logger.debug("Got a 429 from Ollama")
                    if retry_count < MAX_RETRIES:
                        wait_time = (2**retry_count) * RETRY_BASE_SECONDS
                        logger.debug(
                            f"Retry: {retry_count} Waiting {wait_time} seconds before retrying"
                        )
                        await asyncio.sleep(wait_time)

                        return await self.async_get_chat_response(
                            prompt, model, temperature, retry_count + 1
                        )
                    else:
                        raise Exception("Max retries exceeded for Ollama chat API")

                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"Ollama API error: {response.status} - {error_text}")
                    raise Exception(
                        f"Ollama API error: {response.status} - {error_text}"
                    )

                response.raise_for_status()
                resp_json = await response.json()

                # Ollama returns the message in resp_json["message"]["content"]
                if "message" not in resp_json or "content" not in resp_json["message"]:
                    logger.error(f"Unexpected Ollama response format: {resp_json}")
                    raise Exception("Unexpected response format from Ollama")

                msg = resp_json["message"]["content"]
                logger.debug(f"Ollama response: [{msg}]")

                return msg

        except asyncio.TimeoutError:
            logger.error(
                f"Timeout error after {OLLAMA_TIMEOUT_SEC}s when calling Ollama at {self.endpoint}"
            )
            raise Exception(
                f"Ollama request timed out after {OLLAMA_TIMEOUT_SEC}s. Is Ollama running at {self.endpoint}?"
            )
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error when calling Ollama at {self.endpoint}: {e}")
            raise Exception(
                f"Could not connect to Ollama at {self.endpoint}. Is Ollama running? Error: {e}"
            )
        except Exception as e:
            if retry_count < MAX_RETRIES:
                wait_time = (2**retry_count) * RETRY_BASE_SECONDS
                logger.debug(
                    f"Error calling Ollama: {e}. Retry: {retry_count} Waiting {wait_time} seconds"
                )
                await asyncio.sleep(wait_time)
                return await self.async_get_chat_response(
                    prompt, model, temperature, retry_count + 1
                )
            else:
                logger.error(f"Max retries exceeded. Last error: {e}")
                raise

    async def async_get_models(self, retry_count: int = 0) -> list[str]:
        """Fetch the list of available Ollama models from the local endpoint."""
        endpoint = f"{self.endpoint}/api/tags"
        logger.debug(f"Ollama: fetching models from {endpoint} retries {retry_count}")

        try:
            async with (
                aiohttp.ClientSession(timeout=timeout) as session,
                session.get(endpoint) as response,
            ):
                if response.status == 429:
                    logger.debug("Got a 429 from Ollama (tags)")
                    if retry_count < MAX_RETRIES:
                        wait_time = (2**retry_count) * RETRY_BASE_SECONDS
                        logger.debug(
                            f"Retry: {retry_count} Waiting {wait_time} seconds before retrying"
                        )
                        await asyncio.sleep(wait_time)
                        return await self.async_get_models(retry_count + 1)
                    raise Exception("Max retries exceeded for Ollama tags API")

                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(
                        f"Ollama tags API error: {response.status} - {error_text}"
                    )
                    raise Exception(
                        f"Ollama tags API error: {response.status} - {error_text}"
                    )

                response.raise_for_status()
                resp_json = await response.json()
                models = resp_json.get("models", [])
                model_names = [m.get("name") for m in models if m.get("name")]

                logger.debug(f"Ollama models discovered: {model_names}")
                return model_names

        except asyncio.TimeoutError:
            logger.error(
                f"Timeout error after {OLLAMA_TIMEOUT_SEC}s when calling Ollama tags at {self.endpoint}"
            )
            raise Exception(
                f"Ollama tags request timed out after {OLLAMA_TIMEOUT_SEC}s. Is Ollama running at {self.endpoint}?"
            )
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error when calling Ollama tags at {self.endpoint}: {e}")
            raise Exception(
                f"Could not connect to Ollama at {self.endpoint}. Is Ollama running? Error: {e}"
            )
        except Exception as e:
            if retry_count < MAX_RETRIES:
                wait_time = (2**retry_count) * RETRY_BASE_SECONDS
                logger.debug(
                    f"Error calling Ollama tags: {e}. Retry: {retry_count} Waiting {wait_time} seconds"
                )
                await asyncio.sleep(wait_time)
                return await self.async_get_models(retry_count + 1)
            logger.error(f"Max retries exceeded. Last error: {e}")
            raise


ollama_client = OllamaClient()
