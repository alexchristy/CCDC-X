import random
from typing import Callable


def extract_most_duplicate_char_info(string: str) -> dict[str, int | str]:
    """Determine last index of longest duplicated characters in a string.

    Args:
    ----
        string (str): String to search.

    Returns:
    -------
        dict[str, int | str]: Dictionary with string and index of last index of duplicated char. Index set to -1 if there are none.

    """
    if not string:
        return {"string": string, "index": -1}

    max_length = 0
    current_length = 0
    last_indices = []  # To store last indices of tied longest substrings

    for i in range(1, len(string)):
        if string[i] == string[i - 1]:
            current_length += 1
            if current_length > max_length:
                max_length = current_length
                last_indices = [i]  # Start a new list for this new max length
            elif current_length == max_length:
                last_indices.append(i)  # Append this index as a tie
        else:
            current_length = 0  # Reset length counter for new substring

    # Randomly choose a last index in case of a tie
    last_index = random.choice(last_indices) if last_indices else -1  # noqa: S311

    return {"string": string, "index": last_index}


class FilterModule(object):
    """Custom Ansible filter plugin."""

    def filters(self) -> dict[str, Callable[[str], dict[str, int | str]]]:
        """Ansible filter implementation of extract_most_duplicate_char_info."""
        return {
            "extract_most_duplicate_char_info": extract_most_duplicate_char_info,
        }
