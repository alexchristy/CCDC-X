import random


def random_whole_divide(total: int, parts: int) -> list[int]:
    """Divide a number into a random number of whole number of parts.

    If the total is less than the parts, then zeros will be used to
    maintain the total.

    Args:
    ----
        total (int): Number to divide.
        parts (int): Number of whole number parts to divide {total}.

    Returns:
    -------
        list[int]: List of whole number parts that add up to {total}.

    """
    # Zero divided by anything is zero
    if total == 0:
        return [0] * parts

    # Switch to positive and make negative later
    is_negative = total < 0
    total = abs(total)

    # If total is less than parts, fill the list with zeros and distribute total
    if total < parts:
        result = [1] * total + [0] * (parts - total)
        random.shuffle(result)  # Shuffle to randomize the placement of values
    else:
        # Generate (parts - 1) random cut points
        cuts = sorted(random.sample(range(1, total), parts - 1))

        # Include the boundaries (0 and total)
        cuts = [0, *cuts, total]

        # Compute the differences between consecutive cut points
        result = [cuts[i + 1] - cuts[i] for i in range(len(cuts) - 1)]

    # Apply negative sign if total was negative
    if is_negative:
        result = [-x for x in result]

    return result
