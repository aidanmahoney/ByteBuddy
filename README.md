# ByteBuddy
A programming assistant for Discord users.
## Overview
ByteBuddy is a discord bot with programming capabilities. You can add it to your own discord server and prompt it with commands to assist you with coding. It integrates Mixtral's conversational AI to provide expert level coding assistance. It can also compile code and even send memes. The script implements a circular array class which allows the bot store and retrieve previous conversations for contexualized responses.
## Commands
Prefix: `!`
- `meme`: Sends a randomized meme using an API
- `compile [code]`: Compiles code (Currently only Python supported)
- `ask`: Prompts an LLM to assist with coding related questions
## Files
- `main.py`: Contains all methods for a fully functioning Discord bot with coding capabilities
## Requirements
- `Python 3.x`
- `discord`
- `requests`
- `groq`
## Credits
- Aidan Mahoney
- Various sources online
## License

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
