"""Cash register change calculator.

Reads a flat file of transactions (amount_owed,amount_paid) and outputs the
change denominations for each line. Uses minimum denominations unless the
owed amount is divisible by RANDOM_DIVISOR, in which case denominations are
randomly distributed (but mathematically correct).
"""

import random
import sys
from decimal import Decimal

RANDOM_DIVISOR = 3

# (value_in_cents, singular_name, plural_name) — order matters for greedy algorithm
DENOMINATIONS = [
    (100, "dollar", "dollars"),
    (25, "quarter", "quarters"),
    (10, "dime", "dimes"),
    (5, "nickel", "nickels"),
    (1, "penny", "pennies"),
]


def to_cents(amount_str: str) -> int:
    """Convert a dollar-amount string to integer cents."""
    return int(Decimal(amount_str) * 100)


def minimum_change(change_cents: int) -> list[tuple[int, str, str]]:
    """Return denominations using the fewest possible coins/bills (greedy)."""
    result = []
    remaining = change_cents
    for value, singular, plural in DENOMINATIONS:
        count, remaining = divmod(remaining, value)
        result.append((count, singular, plural))
    return result


def random_change(change_cents: int) -> list[tuple[int, str, str]]:
    """Return denominations that sum correctly but are randomly distributed.

    Shuffles all denominations except penny, assigns a random count for each,
    then covers any remainder with pennies so the total is always exact.
    """
    remaining = change_cents
    counts: dict[tuple[str, str], int] = {(s, p): 0 for _, s, p in DENOMINATIONS}

    non_penny = [(v, s, p) for v, s, p in DENOMINATIONS if v > 1]
    random.shuffle(non_penny)

    for value, singular, plural in non_penny:
        if remaining >= value:
            count = random.randint(0, remaining // value)
            counts[(singular, plural)] = count
            remaining -= count * value

    counts[("penny", "pennies")] = remaining

    return [(counts[(s, p)], s, p) for _, s, p in DENOMINATIONS]


def format_change(denominations: list[tuple[int, str, str]]) -> str:
    """Format a denomination list as a comma-separated string, skipping zeros."""
    parts = []
    for count, singular, plural in denominations:
        if count > 0:
            label = singular if count == 1 else plural
            parts.append(f"{count} {label}")
    return ",".join(parts)


def calculate_change(owed_str: str, paid_str: str) -> str:
    """Return the formatted change string for a single transaction."""
    owed_cents = to_cents(owed_str)
    paid_cents = to_cents(paid_str)
    change_cents = paid_cents - owed_cents

    if change_cents < 0:
        raise ValueError(
            f"Amount paid ({paid_str}) is less than amount owed ({owed_str})"
        )

    if owed_cents % RANDOM_DIVISOR == 0:
        denominations = random_change(change_cents)
    else:
        denominations = minimum_change(change_cents)

    return format_change(denominations)


def process_lines(lines: list[str]) -> list[str]:
    """Process an iterable of transaction lines and return change strings."""
    results = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        owed_str, paid_str = line.split(",", 1)
        results.append(calculate_change(owed_str.strip(), paid_str.strip()))
    return results


def process_file(input_path: str) -> list[str]:
    """Read a transaction file and return a list of change strings."""
    with open(input_path) as f:
        return process_lines(f)


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <input_file>", file=sys.stderr)
        sys.exit(1)

    results = process_file(sys.argv[1])
    print("\n".join(results))


if __name__ == "__main__":
    main()
