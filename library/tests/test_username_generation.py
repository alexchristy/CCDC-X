import logging
import re

import pytest

from library.generate_usernames import (
    gen_scheme_username,
    gen_seeded_username,
    validate_username_scheme,
)

###### validate_username_scheme tests ######


def test_validate_username_scheme_valid() -> None:
    """Test validate_username_scheme with valid scheme."""
    valid_schemes = [
        "\\f.\\l+",
        "\\f\\l+",
        "\\f\\l+\\d",
        "\\f\\f.\\l+",
        "\\f\\f\\l+",
        "\\f\\f\\l+\\d\\d\\d",
        "",
        "\\f",
    ]

    for scheme in valid_schemes:
        assert validate_username_scheme(scheme)


def test_validate_username_scheme_invalid() -> None:
    """Test validate_username_scheme with invalid scheme."""
    invalid_schemes = {
        "\\": "Missing meta character after backslash.",
        "\\o": "Invalid meta character 'o'.",
        "\\d+": "Invalid quantifier '+' placement.",
        "+": "Quantifier '+' placed at the beginning of the scheme.",
    }

    for scheme, reason in invalid_schemes.items():
        assert validate_username_scheme(scheme) is False, reason


###### gen_scheme_username tests ######


def test_valid_scheme_username_no_digits() -> None:
    """Test gen_scheme_username with valid scheme with no digits."""
    first_name = "John"
    last_name = "Smith"

    tests = {
        "\\f.\\l+": "j.smith",
        "\\f\\l+": "jsmith",
        "\\f+\\l": "johns",
        "\\f\\f.\\l+": "jo.smith",
        "\\f\\f\\l+": "josmith",
        "\\f+\\f\\l": "johns",  # Once the firstname is consumed no more characters are available
        "\\f.\\l+\\l": "j.smith",  # Once the lastname is consumed no more characters are available
        "\\f-\\l+": "j-smith",
        "\\l.\\f+": "s.john",
        "\\l\\f+": "sjohn",
        "\\l+\\f": "smithj",
        "\\f\\f\\f\\f\\f": "john",
    }

    for scheme, expected in tests.items():
        assert (
            gen_scheme_username(first_name, last_name, scheme, lower=True) == expected
        )


def test_valid_digit_username_schemes() -> None:
    """Test gen_scheme_username with valid digit schemes."""
    first_name = "John"
    last_name = "Smith"

    tests = {
        "\\f\\d": r"j\d",
        "\\f\\d\\d": r"j\d\d",
        "\\f\\d\\d\\d": r"j\d\d\d",
        "\\d\\f": r"\dj",
        "\\f.\\l+\\d": r"j.smith\d",
        "\\f.\\l+\\l\\d": r"j.smith\d",
    }

    for scheme, regex in tests.items():
        pattern = re.compile(regex)
        assert pattern.match(
            gen_scheme_username(first_name, last_name, scheme, lower=True)
        )


def test_invalid_username_schemes() -> None:
    """Test gen_scheme_username with invalid schemes."""
    first_name = "John"
    last_name = "Smith"

    invalid_schemes = {
        "\\": "Missing meta character after backslash.",
        "\\o": "Invalid meta character 'o'.",
        "\\d+": "Invalid quantifier '+' placement.",
        "+": "Quantifier '+' placed at the beginning of the scheme.",
    }

    for scheme, reason in invalid_schemes.items():
        try:
            with pytest.raises(ValueError):
                gen_scheme_username(first_name, last_name, scheme, lower=True)
        except AssertionError:
            pytest.fail(
                f"Expected ValueError was not raised for invalid scheme: {scheme} Reason: {reason}"
            )


def test_missing_first_name() -> None:
    """Test ValueError is raised when first_name arg is not empty."""
    with pytest.raises(ValueError, match="First name and last name must not be empty."):
        gen_scheme_username("", "Smith", "\\f.\\l+")


def test_missing_last_name() -> None:
    """Test ValueError is raised when last_name arg is not empty."""
    with pytest.raises(ValueError, match="First name and last name must not be empty."):
        gen_scheme_username("John", "", "\\f.\\l+")


def test_empty_scheme_warning(caplog: pytest.LogCaptureFixture) -> None:
    """Test that a warning is provided to users when an empty scheme is provided."""
    with caplog.at_level(logging.WARNING):
        gen_scheme_username("John", "Smith", "")

    assert "Scheme is empty. Output will always be empty." in caplog.text
    assert any(record.levelname == "WARNING" for record in caplog.records)


def test_gen_seeded_username_empty_seed() -> None:
    """Test that seeded usernames are generated correctly when only one name is seeded."""
    empty_seeds = ["", " ", "   "]

    tests = {
        "\\f.\\l+": r"[a-z].[a-z]+",
        "\\f+.\\l": r"[a-z]+.[a-z]",
        "\\f.\\l\\l\\l\\d\\d": r"[a-z].[a-z]{3}\d\d",
        "\\f\\l+\\d\\d\\d": r"[a-z]+\d\d",
    }

    for seed in empty_seeds:
        for scheme, regex in tests.items():
            pattern = re.compile(regex)
            assert pattern.match(gen_seeded_username(seed, scheme, lower=True))


def test_gen_seeded_username_first_only() -> None:
    """Test that seeded usernames are generated correctly when only one name is seeded."""
    name = "John"

    tests = {
        "\\f.\\l+": r"j.[a-z]+",
        "\\f+.\\l": r"john.[a-z]",
        "\\f.\\l\\l\\l\\d\\d": r"j.[a-z]{3}\d\d",
        "\\f\\l+\\d\\d\\d": r"j[a-z]+\d\d",
    }

    for scheme, regex in tests.items():
        pattern = re.compile(regex)
        assert pattern.match(gen_seeded_username(name, scheme, lower=True))


def test_gen_seeded_username_first_and_last() -> None:
    """Test that seeded usernames are generated correctly when first and last names are seeded."""
    name = "John Smith"

    tests = {
        "\\f.\\l+": r"j.smith",
        "\\f+.\\l": r"john.s",
        "\\f.\\l\\l\\l\\d\\d": r"j.smi\d\d",
        "\\f\\l+\\d\\d\\d": r"jsmith\d\d",
    }

    for scheme, regex in tests.items():
        pattern = re.compile(regex)
        assert pattern.match(gen_seeded_username(name, scheme, lower=True))


def test_gen_seeded_username_first_middle_and_last() -> None:
    """Test that seeded usernames are generated correctly when first, middle, and last names are seeded."""
    name = "John Adam Smith"

    tests = {
        "\\f.\\l+": r"j.smith",
        "\\f+.\\l": r"john.s",
        "\\f.\\l\\l\\l\\d\\d": r"j.smi\d\d",
        "\\f\\l+\\d\\d\\d": r"jsmith\d\d",
    }

    for scheme, regex in tests.items():
        pattern = re.compile(regex)
        assert pattern.match(gen_seeded_username(name, scheme, lower=True))


def test_gen_seeded_username_more_than_first_middle_and_last() -> None:
    """Test that seeded usernames are generated correctly when more than first, middle, and last names are seeded."""
    name = "John Quincy Adam Smith"

    tests = {
        "\\f.\\l+": r"j.smith",
        "\\f+.\\l": r"john.s",
        "\\f.\\l\\l\\l\\d\\d": r"j.smi\d\d",
        "\\f\\l+\\d\\d\\d": r"jsmith\d\d",
    }

    for scheme, regex in tests.items():
        pattern = re.compile(regex)
        assert pattern.match(gen_seeded_username(name, scheme, lower=True))
