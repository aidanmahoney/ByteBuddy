"""Helper utility functions."""

from ..config import MAX_MESSAGE_LENGTH


def split_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list[str]:
    """
    Split a long message into chunks that fit Discord's limit.

    Args:
        text: The text to split
        max_length: Maximum length for each chunk

    Returns:
        A list of message chunks
    """
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
