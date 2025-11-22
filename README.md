# ByteBuddy

A Discord bot with AI-powered conversational capabilities and entertainment features.

## Overview

ByteBuddy is a Discord bot that integrates Groq's Mixtral LLM to provide intelligent conversational AI assistance. The bot maintains conversation context for each user and includes entertainment features like random meme generation. Built with a modular, well-organized codebase for easy maintenance and extensibility.

## Features

- **AI Conversations**: Ask questions and get intelligent responses powered by Mixtral-8x7b
- **Conversation Memory**: Maintains context for each user's conversation history
- **Meme Generation**: Fetch random memes on demand
- **Rate Limiting**: Prevents spam with per-user rate limiting
- **Error Handling**: Robust error handling and logging throughout

## Commands

All commands use the `!` prefix:

- `!ask <question>`: Ask a question to the AI assistant (maintains conversation context)
- `!reset`: Clear your conversation history with the bot
- `!meme`: Get a random meme from the internet
- `!help`: Display available commands and usage information

## Project Structure

```
ByteBuddy/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # Entry point for the bot
│   ├── config.py            # Configuration and constants
│   ├── bot.py               # ByteBuddy bot class
│   ├── clients/             # API clients
│   │   ├── __init__.py
│   │   ├── groq_client.py   # Groq LLM client
│   │   └── meme_client.py   # Meme API client
│   ├── utils/               # Utility modules
│   │   ├── __init__.py
│   │   ├── message_history.py  # Conversation history manager
│   │   └── helpers.py       # Helper functions
│   └── commands/            # Bot command modules
│       ├── __init__.py
│       ├── ai_commands.py   # AI-related commands
│       └── fun_commands.py  # Entertainment commands
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/aidanmahoney/ByteBuddy.git
   cd ByteBuddy
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file or export the following variables:
   ```bash
   export GROQ_API_KEY="your_groq_api_key"
   export DISCORD_TOKEN="your_discord_bot_token"
   ```

   - Get a Groq API key from [Groq Console](https://console.groq.com/)
   - Create a Discord bot and get token from [Discord Developer Portal](https://discord.com/developers/applications)

4. **Run the bot**:
   ```bash
   python -m src.main
   ```

## Requirements

- Python 3.10+
- discord.py >= 2.3.0
- requests >= 2.31.0
- groq >= 0.4.0

See `requirements.txt` for complete dependency list.

## Configuration

Configuration settings can be modified in `src/config.py`:

- `COMMAND_PREFIX`: Bot command prefix (default: `!`)
- `RATE_LIMIT_SECONDS`: Seconds between commands per user (default: 3)
- `MAX_CONTEXT_MESSAGES`: Maximum conversation history messages (default: 15)
- `MAX_QUESTION_LENGTH`: Maximum question length in characters (default: 500)
- `LLM_MODEL`: The Groq model to use (default: `mixtral-8x7b-32768`)

## Development

The codebase is organized into separate modules for easy maintenance:

- **config.py**: Centralized configuration and environment variables
- **bot.py**: Core bot class with rate limiting and user memory management
- **clients/**: API client wrappers for external services
- **utils/**: Reusable utility functions and classes
- **commands/**: Discord command implementations using Cogs pattern

## License

```
Copyright [2024] [Aidan Mahoney]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## Credits

- Aidan Mahoney
- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Powered by [Groq](https://groq.com/)
