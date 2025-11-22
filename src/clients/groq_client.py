"""Groq API client for LLM interactions."""

import asyncio
import logging
from typing import TYPE_CHECKING

from groq import Groq

from ..config import (
    GROQ_API_KEY,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    LLM_TIMEOUT,
    SYSTEM_PROMPT
)

if TYPE_CHECKING:
    from ..utils.message_history import CircularMessageHistory

logger = logging.getLogger(__name__)


class GroqClient:
    """Client for interacting with Groq's LLM API."""

    def __init__(self):
        """Initialize the Groq client."""
        self.client = Groq(api_key=GROQ_API_KEY)

    async def get_completion(
        self,
        question: str,
        history: "CircularMessageHistory"
    ) -> str:
        """
        Get a completion from the LLM with conversation history.

        Args:
            question: The user's question
            history: The conversation history

        Returns:
            The LLM's response

        Raises:
            asyncio.TimeoutError: If the request times out
            Exception: For other API errors
        """

        def _sync_call():
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(history.get_messages())
            messages.append({"role": "user", "content": question})

            response = self.client.chat.completions.create(
                messages=messages,
                model=LLM_MODEL,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
            )

            return response.choices[0].message.content

        loop = asyncio.get_running_loop()
        return await asyncio.wait_for(
            loop.run_in_executor(None, _sync_call),
            timeout=LLM_TIMEOUT
        )
