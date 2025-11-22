"""Main entry point for ByteBuddy Discord bot."""

import logging

from .bot import ByteBuddy, on_ready, on_command_error
from .config import DISCORD_TOKEN

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the bot."""
    try:
        logger.info("Starting ByteBuddy bot...")

        # Initialize and run bot
        bot = ByteBuddy()

        # Register event listeners
        bot.add_listener(on_ready, "on_ready")
        bot.add_listener(on_command_error, "on_command_error")

        # Start the bot
        bot.run(DISCORD_TOKEN)

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
