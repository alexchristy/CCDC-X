import random

import pytest

from library.generate_groups import (
    APP_MODIFIERS,
    APP_PREFIXES,
    DEPT_GROUP_MODIFIERS,
    DEPT_GROUPS,
    gen_random_app_groups,
    gen_random_dept_groups,
)

###### gen_random_app_groups ######


def test_gen_random_app_groups_negative_groups() -> None:
    """Validate that a ValueError is thrown for num_groups < 0."""
    with pytest.raises(ValueError, match="Number of groups requested less than 0."):
        gen_random_app_groups(-1)


def test_gen_random_app_groups_too_many_groups() -> None:
    """Test that gen_random_app_groups throws ValueError when more groups requested than unique combos."""
    max_combos = len(APP_PREFIXES) * len(APP_MODIFIERS)
    too_many_combos = max_combos + 100

    with pytest.raises(ValueError):
        gen_random_app_groups(too_many_combos)


def test_gen_random_app_groups_valid_groups(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validate that gen_random_app_groups generates valid group names."""
    test_joiner = "|"
    monkeypatch.setattr("library.generate_groups.JOINERS", [test_joiner])

    num_groups = random.randint(1, 10)  # noqa: S311 (Not crypto)

    group_names = gen_random_app_groups(num_groups)

    # Validate all group names are unique
    assert len(group_names) == len(set(group_names))

    # Validate that group names are built with word banks
    for group in group_names:
        assert test_joiner in group

        app_prefix, app_modifier = group.split("|")

        assert app_prefix in APP_PREFIXES
        assert app_modifier in APP_MODIFIERS


###### gen_random_dept_groups ######


def test_gen_random_dept_groups_negative_num_groups() -> None:
    """Validate a ValueError is raised by gen_random_dept_groups when num_groups < 0."""
    with pytest.raises(ValueError, match="Number of groups should be greater than 0"):
        gen_random_dept_groups(-1, 10)


def test_gen_random_dept_groups_no_depts() -> None:
    """Validate a ValueError is raised by gen_random_dept_groups when num_depts < 1."""
    with pytest.raises(ValueError, match="Number of departments should be at least 1"):
        gen_random_dept_groups(10, 0)

    with pytest.raises(ValueError, match="Number of departments should be at least 1"):
        gen_random_dept_groups(10, -1)


def test_gen_random_dept_groups_more_depts_than_bank() -> None:
    """Validate a ValueError is raised by gen_random_dept_groups when num_depts > than DEPT_GROUPS word bank."""
    with pytest.raises(ValueError):
        too_many_depts = len(DEPT_GROUPS) + 100
        gen_random_dept_groups(5, too_many_depts)


def test_gen_random_dept_groups_more_depts_than_groups() -> None:
    """Validate a ValueError is raised by gen_random_dept_groups when num_depts > num_groups."""
    with pytest.raises(
        ValueError, match="Too many departments! Ensure num_groups >= num_depts"
    ):
        num_groups = random.randint(5, 20)  # noqa: S311 (Not crypto)
        num_depts = num_groups + 5

        gen_random_dept_groups(num_groups, num_depts)


def test_gen_random_dept_groups_too_many_combos() -> None:
    """Validate a ValueError is raised by gen_random_dept_groups when more groups are requested than possible unique group names based on word bank."""
    max_combos = len(DEPT_GROUPS) * len(DEPT_GROUP_MODIFIERS)
    too_many_combos = max_combos + 100

    with pytest.raises(ValueError):
        gen_random_dept_groups(too_many_combos, 10)


def test_gen_random_dept_groups_valid_group_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that gen_random_dept_groups generates valid group names using the word banks."""
    test_joiner = "|"
    monkeypatch.setattr("library.generate_groups.JOINERS", [test_joiner])

    num_groups = random.randint(2, 10)  # noqa: S311 (Not crypto)
    num_depts = num_groups // 2

    group_names = gen_random_dept_groups(num_groups, num_depts)

    # Validate all group names are unique
    assert len(group_names) == len(set(group_names))

    # Validate that group names are built with word banks
    for group in group_names:
        # Modified group names
        if test_joiner in group:
            dept_group, dept_modifier = group.split("|")

            assert dept_group in DEPT_GROUPS
            assert dept_modifier in DEPT_GROUP_MODIFIERS
        else:  # Base dept group
            assert group in DEPT_GROUPS
