import random

from ..random_utils import random_whole_divide

###### random_whole_divide ######


def test_random_whole_divide_zero_total() -> None:
    """Validate that random_whole_divide returns zeros when total is zero."""
    parts = random.randint(1, 100)  # noqa: S311 (Not crypto)
    result = random_whole_divide(0, parts)

    assert len(result) == parts
    assert all(part == 0 for part in result)


def test_random_whole_divide_parts_greater_than_total_positive() -> None:
    """Validate that random_whole_divide returns a valid list when total < parts and total > 0."""
    parts = random.randint(20, 100)  # noqa: S311 (Not crypto)
    total = parts - random.randint(1, 19)  # noqa: S311 (Not crypto)

    result = random_whole_divide(total, parts)

    assert len(result) == parts
    assert sum(result) == total


def test_random_whole_divide_parts_greater_than_total_negative() -> None:
    """Validate that random_whole_divide returns a valid list when total < parts and total < 0."""
    parts = random.randint(20, 100)  # noqa: S311 (Not crypto)
    total = -(parts - random.randint(1, 19))  # noqa: S311 (Not crypto)

    result = random_whole_divide(total, parts)

    assert len(result) == parts
    assert sum(result) == total


def test_random_whole_divide_total_greater_than_parts_positive() -> None:
    """Validate that random_whole_divide returns a valid list when total > parts and total > 0."""
    parts = random.randint(20, 100)  # noqa: S311 (Not crypto)
    total = random.randint(150, 200)  # noqa: S311 (Not crypto)

    result = random_whole_divide(total, parts)

    assert len(result) == parts
    assert sum(result) == total


def test_random_whole_divide_total_greater_than_parts_negative() -> None:
    """Validate that random_whole_divide returns a valid list when total > parts and total < 0."""
    parts = random.randint(20, 100)  # noqa: S311 (Not crypto)
    total = random.randint(-250, -200)  # noqa: S311 (Not crypto)

    result = random_whole_divide(total, parts)

    assert len(result) == parts
    assert sum(result) == total
