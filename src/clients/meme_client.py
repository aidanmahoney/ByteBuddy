"""Meme API client for fetching random memes."""

import asyncio
import logging
from typing import Optional

import requests

from ..config import MEME_API_URL, HTTP_TIMEOUT

logger = logging.getLogger(__name__)


class MemeClient:
    """Client for fetching memes from the meme API."""

    @staticmethod
    async def fetch_meme() -> Optional[str]:
        """
        Fetch a random meme URL from the API.

        Returns:
            The meme URL if successful, None otherwise

        Raises:
            Exception: For API errors
        """

        def _sync_fetch():
            response = requests.get(MEME_API_URL, timeout=HTTP_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            return data.get("url")

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _sync_fetch)
