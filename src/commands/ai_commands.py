"""AI-related bot commands."""

import asyncio
import logging

from discord.ext import commands

from ..clients import GroqClient
from ..config import MAX_QUESTION_LENGTH
from ..utils import split_message

logger = logging.getLogger(__name__)


class AICommands(commands.Cog):
    """Commands for AI interactions."""

    def __init__(self, bot):
        """
        Initialize the AI commands cog.

        Args:
            bot: The ByteBuddy bot instance
        """
        self.bot = bot
        self.groq_client = GroqClient()

    @commands.command(name="ask", help="Ask a question to the AI assistant")
    async def ask(self, ctx: commands.Context, *, question: str):
        """
        Ask a question to the LLM.

        Args:
            ctx: The command context
            question: The question to ask
        """
        try:
            # Rate limiting
            if not self.bot.check_rate_limit(ctx.author.id):
                await ctx.send("Please wait a moment before asking another question.")
                return

            # Validate question length
            if len(question) > MAX_QUESTION_LENGTH:
                await ctx.send(
                    f"Question is too long. Please keep it under {MAX_QUESTION_LENGTH} characters."
                )
                return

            # Show typing indicator
            async with ctx.typing():
                # Get user's conversation history
                history = self.bot.get_user_history(ctx.author.id)

                # Call LLM
                answer = await self.groq_client.get_completion(question, history)

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

    @commands.command(name="reset", help="Clear your conversation history")
    async def reset(self, ctx: commands.Context):
        """
        Clear the user's conversation history.

        Args:
            ctx: The command context
        """
        try:
            user_id = ctx.author.id
            if user_id in self.bot.user_memories:
                self.bot.user_memories[user_id].clear()
                await ctx.send("Your conversation history has been cleared.")
            else:
                await ctx.send("You don't have any conversation history yet.")

        except Exception as e:
            await ctx.send("Failed to reset conversation history.")
            logger.error(f"Error in reset command: {e}", exc_info=True)


async def setup(bot):
    """
    Setup function for the cog.

    Args:
        bot: The ByteBuddy bot instance
    """
    await bot.add_cog(AICommands(bot))
