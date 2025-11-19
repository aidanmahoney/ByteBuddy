import os
import asyncio
import logging
from typing import Optional

import discord
import requests
from discord.ext import commands
from groq import Groq

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MEME_API = "https://meme-api.com/gimme"

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is required")

client = Groq(api_key=GROQ_API_KEY)

MAX_MESSAGE_LENGTH = 1900
MAX_CONTEXT_MESSAGES = 15
LLM_TIMEOUT = 30
HTTP_TIMEOUT = 10
MAX_QUESTION_LENGTH = 500

class CircularMessageHistory:
    """Stores a circular buffer of conversation messages."""
    
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.messages = []
    
    def add_message(self, role: str, content: str):
        """Add a message to history."""
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_size:
            self.messages.pop(0)
    
    def get_messages(self):
        """Get all messages in history."""
        return self.messages.copy()
    
    def clear(self):
        """Clear all messages."""
        self.messages.clear()

class ByteBuddy(commands.Bot):
    """A safe Discord bot with LLM and meme capabilities."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=commands.DefaultHelpCommand()
        )
        
        # Store user conversation histories
        self.user_memories = {}
        
        # Rate limiting: track last command time per user
        self.rate_limits = {}
        self.rate_limit_seconds = 3
    
    async def setup_hook(self):
        """Called when the bot is starting up."""
        logger.info("Bot is setting up...")
    
    def check_rate_limit(self, user_id: int) -> bool:
        """Check if user is rate limited."""
        import time
        current_time = time.time()
        
        if user_id in self.rate_limits:
            last_time = self.rate_limits[user_id]
            if current_time - last_time < self.rate_limit_seconds:
                return False
        
        self.rate_limits[user_id] = current_time
        return True
    
    def get_user_history(self, user_id: int) -> CircularMessageHistory:
        """Get or create conversation history for a user."""
        if user_id not in self.user_memories:
            self.user_memories[user_id] = CircularMessageHistory(MAX_CONTEXT_MESSAGES)
        return self.user_memories[user_id]


# Initialize bot
bot = ByteBuddy()

async def call_llm(question: str, history: CircularMessageHistory) -> str:
    """Call the Groq LLM with conversation history."""
    
    def _sync_call():
        system_prompt = (
            "You are a helpful, knowledgeable assistant named ByteBuddy. "
            "Provide clear, accurate, and concise answers. "
            "If you're unsure about something, say so. "
            "Keep responses under 1500 characters when possible."
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history.get_messages())
        messages.append({"role": "user", "content": question})
        
        response = client.chat.completions.create(
            messages=messages,
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=1000,
        )
        
        return response.choices[0].message.content
    
    loop = asyncio.get_running_loop()
    return await asyncio.wait_for(
        loop.run_in_executor(None, _sync_call),
        timeout=LLM_TIMEOUT
    )


async def fetch_meme() -> Optional[str]:
    """Fetch a random meme from the API."""
    
    def _sync_fetch():
        response = requests.get(MEME_API, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data.get("url")
    
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _sync_fetch)


def split_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list[str]:
    """Split a long message into chunks that fit Discord's limit."""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break
        
        # Try to split at a newline
        split_pos = text.rfind('\n', 0, max_length)
        if split_pos == -1:
            # No newline, split at last space
            split_pos = text.rfind(' ', 0, max_length)
        if split_pos == -1:
            # No space either, hard split
            split_pos = max_length
        
        chunks.append(text[:split_pos])
        text = text[split_pos:].lstrip()
    
    return chunks


@bot.event
async def on_ready():
    """Called when the bot successfully connects to Discord."""
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} guilds")
    print(f"Bot is ready! Logged in as {bot.user}")


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """Global error handler for commands."""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: `{error.param.name}`")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Please wait {error.retry_after:.1f} seconds before using this command again.")
    else:
        logger.error(f"Command error: {error}", exc_info=error)
        await ctx.send("An error occurred while processing your command.")

@bot.command(name="ask", help="Ask a question to the AI assistant")
async def ask(ctx: commands.Context, *, question: str):
    """Ask a question to the LLM."""
    try:
        # Rate limiting
        if not bot.check_rate_limit(ctx.author.id):
            await ctx.send("Please wait a moment before asking another question.")
            return
        
        # Validate question length
        if len(question) > MAX_QUESTION_LENGTH:
            await ctx.send(f"Question is too long. Please keep it under {MAX_QUESTION_LENGTH} characters.")
            return
        
        # Show typing indicator
        async with ctx.typing():
            # Get user's conversation history
            history = bot.get_user_history(ctx.author.id)
            
            # Call LLM
            answer = await call_llm(question, history)
            
            # Update history
            history.add_message("user", question)
            history.add_message("assistant", answer)
        
        # Split and send response
        chunks = split_message(answer)
        for chunk in chunks:
            await ctx.send(chunk)
    
    except asyncio.TimeoutError:
        await ctx.send("Request timed out. Please try again.")
        logger.error("LLM request timed out")
    
    except Exception as e:
        await ctx.send("Failed to get a response. Please try again later.")
        logger.error(f"Error in ask command: {e}", exc_info=True)


@bot.command(name="reset", help="Clear your conversation history")
async def reset(ctx: commands.Context):
    """Clear the user's conversation history."""
    try:
        user_id = ctx.author.id
        if user_id in bot.user_memories:
            bot.user_memories[user_id].clear()
            await ctx.send("Your conversation history has been cleared.")
        else:
            await ctx.send("You don't have any conversation history yet.")
    
    except Exception as e:
        await ctx.send("Failed to reset conversation history.")
        logger.error(f"Error in reset command: {e}", exc_info=True)


@bot.command(name="meme", help="Get a random meme")
async def meme(ctx: commands.Context):
    """Fetch and send a random meme."""
    try:
        # Rate limiting
        if not bot.check_rate_limit(ctx.author.id):
            await ctx.send("Please wait a moment before requesting another meme.")
            return
        
        async with ctx.typing():
            url = await fetch_meme()
        
        if url:
            embed = discord.Embed(title="Random Meme", color=discord.Color.random())
            embed.set_image(url=url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Could not fetch a meme URL.")
    
    except asyncio.TimeoutError:
        await ctx.send("Request timed out. Please try again.")
        logger.error("Meme request timed out")
    
    except Exception as e:
        await ctx.send("Failed to fetch a meme. Please try again later.")
        logger.error(f"Error in meme command: {e}", exc_info=True)


@bot.command(name="help", help="Show available commands")
async def help_command(ctx: commands.Context):
    """Show help information."""
    embed = discord.Embed(
        title="Bot Commands",
        description="Here are the available commands:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="!ask <question>",
        value="Ask a question to the AI assistant. The bot remembers your conversation context.",
        inline=False
    )
    
    embed.add_field(
        name="!reset",
        value="Clear your conversation history with the bot.",
        inline=False
    )
    
    embed.add_field(
        name="!meme",
        value="Get a random meme from the internet.",
        inline=False
    )
    
    embed.add_field(
        name="!help",
        value="Show this help message.",
        inline=False
    )
    
    embed.set_footer(text="Rate limit: One command every 3 seconds per user")
    
    await ctx.send(embed=embed)


def main():
    """Main entry point for the bot."""
    try:
        logger.info("Starting bot...")
        bot.run(DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

