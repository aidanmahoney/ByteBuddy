"""Fun/entertainment bot commands."""

import asyncio
import logging

import discord
from discord.ext import commands

from ..clients import MemeClient

logger = logging.getLogger(__name__)


class FunCommands(commands.Cog):
    """Commands for fun and entertainment."""

    def __init__(self, bot):
        """
        Initialize the fun commands cog.

        Args:
            bot: The ByteBuddy bot instance
        """
        self.bot = bot
        self.meme_client = MemeClient()

    @commands.command(name="meme", help="Get a random meme")
    async def meme(self, ctx: commands.Context):
        """
        Fetch and send a random meme.

        Args:
            ctx: The command context
        """
        try:
            # Rate limiting
            if not self.bot.check_rate_limit(ctx.author.id):
                await ctx.send("Please wait a moment before requesting another meme.")
                return

            async with ctx.typing():
                url = await self.meme_client.fetch_meme()

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

    @commands.command(name="help", help="Show available commands")
    async def help_command(self, ctx: commands.Context):
        """
        Show help information.

        Args:
            ctx: The command context
        """
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


async def setup(bot):
    """
    Setup function for the cog.

    Args:
        bot: The ByteBuddy bot instance
    """
    await bot.add_cog(FunCommands(bot))
