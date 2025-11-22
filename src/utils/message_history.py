"""Circular message history for maintaining conversation context."""


class CircularMessageHistory:
    """Stores a circular buffer of conversation messages."""

    def __init__(self, max_size: int):
        """
        Initialize the message history.

        Args:
            max_size: Maximum number of messages to store
        """
        self.max_size = max_size
        self.messages = []

    def add_message(self, role: str, content: str):
        """
        Add a message to history.

        Args:
            role: The role of the message sender (e.g., "user", "assistant")
            content: The message content
        """
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_size:
            self.messages.pop(0)

    def get_messages(self):
        """
        Get all messages in history.

        Returns:
            A copy of the messages list
        """
        return self.messages.copy()

    def clear(self):
        """Clear all messages from history."""
        self.messages.clear()
