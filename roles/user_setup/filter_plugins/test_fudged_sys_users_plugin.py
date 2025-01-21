from random import seed

from fudged_sys_users_plugin import (
    extract_most_duplicate_char_info,
)

###### extract_most_duplicate_char_info tests ######


def test_no_duplicates() -> None:
    """Test with a string that has no duplicated characters."""
    string = "abcdef"
    result = extract_most_duplicate_char_info(string)
    assert result == {"string": string, "index": -1}


def test_single_duplicate_pair() -> None:
    """Test with a string that has a single pair of duplicated characters."""
    string = "abccdef"
    result = extract_most_duplicate_char_info(string)
    assert result == {"string": string, "index": 3}


def test_multiple_duplicate_pairs() -> None:
    """Test with a string that has multiple duplicate substrings."""
    string = "aabbccddeeff"
    result = extract_most_duplicate_char_info(string)
    assert result["string"] == string
    assert result["index"] in {1, 3, 5, 7, 9, 11}


def test_longest_duplicate_substring() -> None:
    """Test with a string that has one longest duplicated substring."""
    string = "Whoopsss"
    result = extract_most_duplicate_char_info(string)
    assert result == {"string": string, "index": 7}


def test_tied_longest_duplicates() -> None:
    """Test with a string that has tied longest duplicate substrings."""
    string = "aaaabbbb"
    seed(42)  # Fix the random seed for predictable results in testing
    result = extract_most_duplicate_char_info(string)
    assert result["string"] == string
    assert result["index"] in {3, 7}  # Indices of tied substrings


def test_random_selection_on_tie() -> None:
    """Test that a random index is selected when duplicate substrings are tied."""
    string = "aabbcc"
    indices_seen = set()
    for _ in range(100):
        result = extract_most_duplicate_char_info(string)
        indices_seen.add(result["index"])
    assert indices_seen == {1, 3, 5}  # All tied indices are eventually seen


def test_empty_string() -> None:
    """Test with an empty string."""
    string = ""
    result = extract_most_duplicate_char_info(string)
    assert result == {"string": string, "index": -1}


def test_single_character_string() -> None:
    """Test with a string that has only one character."""
    string = "a"
    result = extract_most_duplicate_char_info(string)
    assert result == {"string": string, "index": -1}


def test_all_characters_duplicated() -> None:
    """Test with a string where all characters are duplicated."""
    string = "aabbccddeeffgg"
    result = extract_most_duplicate_char_info(string)
    assert result["string"] == string
    assert result["index"] in {1, 3, 5, 7, 9, 11, 13}


def test_single_long_duplicate_substring() -> None:
    """Test with a string that has a single long duplicated substring."""
    string = "aabbbbbcc"
    result = extract_most_duplicate_char_info(string)
    assert result == {"string": string, "index": 6}


def test_mixed_case_duplicates() -> None:
    """Test with a string that has mixed case duplicates."""
    string = "AaBbCcDd"
    result = extract_most_duplicate_char_info(string)
    assert result == {"string": string, "index": -1}


def test_duplicates_at_start() -> None:
    """Test with duplicates at the start of the string."""
    string = "aabcde"
    result = extract_most_duplicate_char_info(string)
    assert result == {"string": string, "index": 1}


def test_duplicates_at_end() -> None:
    """Test with duplicates at the end of the string."""
    string = "abcdeff"
    result = extract_most_duplicate_char_info(string)
    assert result == {"string": string, "index": 6}


def test_non_alphabetic_duplicates() -> None:
    """Test with non-alphabetic characters."""
    string = "112233445566"
    result = extract_most_duplicate_char_info(string)
    assert result["string"] == string
    assert result["index"] in {1, 3, 5, 7, 9, 11}
