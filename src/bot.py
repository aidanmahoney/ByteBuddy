"""ByteBuddy Discord bot class."""

import logging
import time

import discord
from discord.ext import commands

from .config import COMMAND_PREFIX, RATE_LIMIT_SECONDS, MAX_CONTEXT_MESSAGES
from .utils import CircularMessageHistory

logger = logging.getLogger(__name__)


class ByteBuddy(commands.Bot):
    """A Discord bot with LLM and entertainment capabilities."""

    def __init__(self):
        """Initialize the ByteBuddy bot."""
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=None
        )

        # Store user conversation histories
        self.user_memories = {}

        # Rate limiting: track last command time per user
        self.rate_limits = {}
        self.rate_limit_seconds = RATE_LIMIT_SECONDS

    async def setup_hook(self):
        """Called when the bot is starting up."""
        logger.info("Bot is setting up...")

        # Load command cogs
        await self.load_extension("src.commands.ai_commands")
        await self.load_extension("src.commands.fun_commands")

        logger.info("All cogs loaded successfully")

    def check_rate_limit(self, user_id: int) -> bool:
        """
        Check if user is rate limited.

        Args:
            user_id: The Discord user ID

        Returns:
            True if the user can proceed, False if rate limited
        """
        current_time = time.time()

        if user_id in self.rate_limits:
            last_time = self.rate_limits[user_id]
            if current_time - last_time < self.rate_limit_seconds:
                return False

        self.rate_limits[user_id] = current_time
        return True

    def get_user_history(self, user_id: int) -> CircularMessageHistory:
        """
        Get or create conversation history for a user.

        Args:
            user_id: The Discord user ID

        Returns:
            The user's conversation history
        """
        if user_id not in self.user_memories:
            self.user_memories[user_id] = CircularMessageHistory(MAX_CONTEXT_MESSAGES)
        return self.user_memories[user_id]


@commands.Cog.listener()
async def on_ready(bot):
    """Called when the bot successfully connects to Discord."""
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} guilds")
    print(f"Bot is ready! Logged in as {bot.user}")


@commands.Cog.listener()
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """
    Global error handler for commands.

    Args:
        ctx: The command context
        error: The error that occurred
    """
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: `{error.param.name}`")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"Please wait {error.retry_after:.1f} seconds before using this command again."
        )
    else:
        logger.error(f"Command error: {error}", exc_info=error)
        await ctx.send("An error occurred while processing your command.")
