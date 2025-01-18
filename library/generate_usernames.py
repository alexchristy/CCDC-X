import logging
from random import randint

import names as name_db
from ansible.module_utils.basic import AnsibleModule

logger = logging.getLogger(__name__)

# Constants
FIRST_NAME_META_CHAR = "f"
LAST_NAME_META_CHAR = "l"
DIGIT_META_CHAR = "d"
FULL_QUANTIFIER = "+"

# Grouped constants
META_CHARS = [FIRST_NAME_META_CHAR, LAST_NAME_META_CHAR, DIGIT_META_CHAR]
QUANTFIABLE_META_CHARS = [FIRST_NAME_META_CHAR, LAST_NAME_META_CHAR]
QUANTIFIERS = [FULL_QUANTIFIER]


def validate_username_scheme(scheme: str) -> bool:
    r"""Validate the username scheme.

    The scheme is defined with a rudimentary regex pattern. Accepts arbitrary
    characeters and the following placeholders:

    Scheme Regex Character Classes:
    ------------------------------
    \f: Letter of a firstname.
    \l: Letter of a lastname.
    \d: Random digit 0 to 9.

    Quantifiers:
    -----------
    +: Entire name. Used with \f or \l.

    Args:
    ----
        scheme (str): Username scheme.

    Returns:
    -------
        bool: True if the scheme is valid, False otherwise.

    """
    # Validate meta characters
    meta_char_parts = scheme.split("\\")

    # First split can be ignored
    for part in meta_char_parts[1:]:
        try:
            if part[0] not in META_CHARS:
                logger.error("Invalid meta character: '%s' ", part[0])
                return False
        except Exception as e:
            logger.error("An unexpected error occurred: %s", e)
            return False

    # Validate quantifiers
    for quantifier in QUANTIFIERS:
        quantifier_parts = scheme.split(quantifier)

        # Last split can be ignored
        for part in quantifier_parts[:-1]:
            try:
                if part[-1] not in QUANTFIABLE_META_CHARS:
                    logger.error(
                        "Invalid quantifier placement. Quantifier: '%s' placed after non-quantifiable character: '%s' ",
                        quantifier,
                        part[-1],
                    )
                    return False
            except IndexError:
                logger.error(
                    "Invalid quantifier placement. Quantifier: '%s' placed at the beginning of the scheme.",
                    quantifier,
                )
                return False
            except Exception as e:
                logger.error("An unexpected error occurred: %s", e)
                return False

    logger.info("Username scheme: '%s' is valid.", scheme)

    return True


def gen_scheme_username(
    first_name: str,
    last_name: str,
    scheme: str,
    lower: bool = True,
) -> str:
    r"""Generate a username according to the scheme.

    The scheme is defined with a rudimentary regex pattern. Accepts arbitrary
    characeters and the following placeholders:

    Scheme Regex Character Classes:
    ------------------------------
    \\f: Letter of a firstname.
    \\l: Letter of a lastname.
    \\d: Random digit 0 to 9.

    Quantifiers:
    -----------
    +: Entire name. Used with \\f or \\l. (Puts the rest of the name if \\f has been used earlier in the scheme.)

    Args:
    ----
        first_name (str): First name of the user.
        last_name (str): Last name of the user.
        scheme (str): Username scheme.
        lower (bool): Convert the generated username to lowercase. Default is True.

    Returns:
    -------
        str: Generated username.

    Raises:
    ------
        ValueError: If the scheme is invalid or if first_name or last_name are empty.

    """
    # Validate the scheme
    if not validate_username_scheme(scheme):
        msg = f"Invalid username scheme: '{scheme}'."
        logger.error(msg)
        raise ValueError(msg)

    # Validate the first and last name
    if not first_name or not last_name:
        msg = "First name and last name must not be empty."
        logger.error(msg)
        raise ValueError(msg)

    if not scheme:
        logger.warning("Scheme is empty. Output will always be empty.")

    # Generate the username
    scheme_parts = scheme.split("\\")

    # First part can't be a meta character
    username = scheme_parts[0]

    for part in scheme_parts[1:]:
        meta_char = part[0]

        try:
            has_quantifier = part[1] in QUANTIFIERS
        except IndexError:
            has_quantifier = False

        if meta_char == FIRST_NAME_META_CHAR:
            if has_quantifier:
                username += first_name
                first_name = ""  # Remove the first name
            elif first_name:  # If the username is not empty
                username += first_name[0]
                first_name = first_name[1:]  # Remove the first character
        elif meta_char == LAST_NAME_META_CHAR:
            if has_quantifier:
                username += last_name
                last_name = ""
            elif last_name:
                username += last_name[0]
                last_name = last_name[1:]
        elif meta_char == DIGIT_META_CHAR:
            username += str(randint(0, 9))  # noqa: S311 (Not crypto)

        # Remove quantifier from the scheme part
        if has_quantifier:
            username += part[2:]
        else:
            username += part[1:]

    if lower:
        username = username.lower()

    return username


def gen_seeded_username(name_seed: str, scheme: str, lower: bool = True) -> str:
    """Generate a username based on a seed and a scheme.

    This function assumes that names follow the structure of First, Middle (Optional), Last. If
    a name has more than a First, Middle, and Last name then the First name will be selected from
    the first name provided and the last name will be select from the last name provided.

    Ex:
    - name="John" --> first_name="John" last_name="{Random last name from census DB}
    - name="John Smith" --> first_name="John" last_name="Smith"
    - name="John Adams Smith" --> first_name="John" last_name="Smith"
    - name="John Quincy Adam Smith" --> first_name="John" last_name="Smith"

    Args:
    ----
        name_seed (str): Name that will act as the seed for the generated username.
        scheme (str): Scheme to generate the username with.
        lower (bool): Whether or not username should be made lowercase.

    Returns:
    -------
        str: Generated username based on seed conforming to scheme.

    Raises:
    ------
        ValueError: Scheme is invalid.

    """
    len_first_only = 1
    len_first_last = 2
    len_first_middle_last = 3

    names = name_seed.strip().split(" ")

    # Parse seed
    if len(names) == len_first_only:
        if not names[0]:
            first_name, last_name = name_db.get_full_name().split(" ")
        else:
            first_name = names[0]
            last_name = name_db.get_last_name()
    elif len(names) == len_first_last:
        first_name = names[0]
        last_name = names[1]
    elif len(names) == len_first_middle_last:
        first_name = names[0]
        last_name = names[2]
    else:
        first_name = names[0]
        last_name = names[-1]

    return gen_scheme_username(first_name, last_name, scheme, lower=lower)


def run() -> None:  # pragma: no cover
    """Run the custom Anisble module."""
    module = AnsibleModule(
        argument_spec=dict(
            number=dict(type="int", required=True),
            scheme=dict(type="str", required=True),
            name_seeds=dict(type="list", elements="str", required=False),
            existing_usernames=dict(type="list", elements="str", required=False),
            lowercase=dict(type="bool", required=False, default=True),
        )
    )

    # Ansible args typed
    name_seeds: list[str] = module.params["name_seeds"]
    req_num_usernames: int = module.params["number"]
    scheme: str = module.params["scheme"]
    existing_usernames = (
        set(module.params["existing_usernames"])
        if module.params["existing_usernames"]
        else set()
    )
    lowercase_choice: bool = module.params["lowercase"]

    usernames = existing_usernames.copy()

    try:
        # Generate seeded usernames
        if name_seeds:
            for name in name_seeds:
                if len(usernames - existing_usernames) >= req_num_usernames:
                    break

                usernames.add(gen_seeded_username(name, scheme, lower=lowercase_choice))

        # Generate random usernames to reach requested number of usernames
        while len(usernames - existing_usernames) < req_num_usernames:
            first_name, last_name = name_db.get_full_name().split(" ")
            usernames.add(
                gen_scheme_username(
                    first_name, last_name, scheme, lower=lowercase_choice
                )
            )
    except Exception as e:
        module.fail_json(msg=f"Failed to generate usernames: {e}")

    dedup_usernames = usernames - existing_usernames

    result = {
        "changed": False,
        "msg": f"Generated {len(dedup_usernames)} usernames",
        "usernames": dedup_usernames,
    }

    module.exit_json(**result)


if __name__ == "__main__":  # pragma: no cover
    run()
