"""Configuration settings for ByteBuddy bot."""

import os
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# API Keys and tokens
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Validate required environment variables
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is required")

# API endpoints
MEME_API_URL = "https://meme-api.com/gimme"

# Bot configuration
COMMAND_PREFIX = "!"

# Rate limiting
RATE_LIMIT_SECONDS = 3

# Message limits
MAX_MESSAGE_LENGTH = 1900
MAX_QUESTION_LENGTH = 500
MAX_CONTEXT_MESSAGES = 15

# Timeouts
LLM_TIMEOUT = 30
HTTP_TIMEOUT = 10

# LLM settings
LLM_MODEL = "mixtral-8x7b-32768"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 1000

# System prompt for the AI
SYSTEM_PROMPT = (
    "You are a helpful, knowledgeable assistant named ByteBuddy. "
    "Provide clear, accurate, and concise answers. "
    "If you're unsure about something, say so. "
    "Keep responses under 1500 characters when possible."
)
