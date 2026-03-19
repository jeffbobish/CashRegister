"""Unit tests for cash_register.py."""

import unittest

from cash_register import (
    RANDOM_DIVISOR,
    calculate_change,
    format_change,
    minimum_change,
    process_lines,
    random_change,
    to_cents,
)

# Map denomination singular names to cent values for result verification
CENT_VALUES = {"dollar": 100, "quarter": 25, "dime": 10, "nickel": 5, "penny": 1}


def total_cents(denominations: list[tuple[int, str, str]]) -> int:
    return sum(count * CENT_VALUES[singular] for count, singular, _ in denominations)


def parse_change_string(change_str: str) -> int:
    """Parse a formatted change string back to total cents."""
    if not change_str:
        return 0
    value_map = {
        "dollar": 100, "dollars": 100,
        "quarter": 25, "quarters": 25,
        "dime": 10, "dimes": 10,
        "nickel": 5, "nickels": 5,
        "penny": 1, "pennies": 1,
    }
    total = 0
    for part in change_str.split(","):
        count_str, unit = part.strip().split(" ", 1)
        total += int(count_str) * value_map[unit]
    return total


class TestToCents(unittest.TestCase):
    def test_whole_dollar(self):
        self.assertEqual(to_cents("3.00"), 300)

    def test_dollars_and_cents(self):
        self.assertEqual(to_cents("2.12"), 212)

    def test_less_than_one_dollar(self):
        self.assertEqual(to_cents("0.99"), 99)


class TestMinimumChange(unittest.TestCase):
    def test_88_cents_matches_sample_output(self):
        """2.12 owed, 3.00 paid → 88 cents → 3 quarters, 1 dime, 3 pennies."""
        result = minimum_change(88)
        counts = {coin: count for count, coin, _ in result}
        self.assertEqual(counts["quarter"], 3)
        self.assertEqual(counts["dime"], 1)
        self.assertEqual(counts["nickel"], 0)
        self.assertEqual(counts["penny"], 3)

    def test_3_cents_matches_sample_output(self):
        result = minimum_change(3)
        counts = {coin: count for count, coin, _ in result}
        self.assertEqual(counts["penny"], 3)
        self.assertEqual(counts["quarter"], 0)
        self.assertEqual(counts["dollar"], 0)

    def test_167_cents(self):
        """1 dollar, 2 quarters, 1 dime, 1 nickel, 2 pennies."""
        result = minimum_change(167)
        counts = {coin: count for count, coin, _ in result}
        self.assertEqual(counts["dollar"], 1)
        self.assertEqual(counts["quarter"], 2)
        self.assertEqual(counts["dime"], 1)
        self.assertEqual(counts["nickel"], 1)
        self.assertEqual(counts["penny"], 2)

    def test_zero_change(self):
        result = minimum_change(0)
        self.assertEqual(total_cents(result), 0)
        # All counts are zero
        self.assertTrue(all(c == 0 for c, _, _ in result))

    def test_total_is_always_correct(self):
        for cents in [1, 5, 10, 25, 50, 99, 100, 199, 500]:
            with self.subTest(cents=cents):
                self.assertEqual(total_cents(minimum_change(cents)), cents)


class TestRandomChange(unittest.TestCase):
    def test_sum_is_always_correct(self):
        for _ in range(50):
            result = random_change(167)
            self.assertEqual(total_cents(result), 167)

    def test_all_counts_non_negative(self):
        for _ in range(50):
            result = random_change(88)
            self.assertTrue(all(c >= 0 for c, _, _ in result))

    def test_zero_change(self):
        result = random_change(0)
        self.assertEqual(total_cents(result), 0)

    def test_produces_variety_over_runs(self):
        """With 10 runs, the outputs should not all be identical (extremely unlikely)."""
        results = [format_change(random_change(167)) for _ in range(10)]
        self.assertGreater(len(set(results)), 1)


class TestFormatChange(unittest.TestCase):
    def test_singular_label(self):
        result = format_change([(1, "dollar", "dollars"), (0, "quarter", "quarters")])
        self.assertEqual(result, "1 dollar")

    def test_plural_label(self):
        result = format_change([(0, "dollar", "dollars"), (3, "penny", "pennies")])
        self.assertEqual(result, "3 pennies")

    def test_skips_zero_counts(self):
        result = format_change([(0, "dollar", "dollars"), (2, "quarter", "quarters")])
        self.assertNotIn("dollar", result)
        self.assertEqual(result, "2 quarters")

    def test_multiple_denominations_comma_separated(self):
        result = format_change([
            (1, "dollar", "dollars"),
            (1, "quarter", "quarters"),
            (0, "dime", "dimes"),
        ])
        self.assertEqual(result, "1 dollar,1 quarter")

    def test_all_zeros_returns_empty_string(self):
        result = format_change([(0, "dollar", "dollars"), (0, "penny", "pennies")])
        self.assertEqual(result, "")


class TestCalculateChange(unittest.TestCase):
    def test_minimum_change_sample_1(self):
        """2.12 owed: 212 % 3 != 0 → minimum → "3 quarters,1 dime,3 pennies"."""
        self.assertEqual(calculate_change("2.12", "3.00"), "3 quarters,1 dime,3 pennies")

    def test_minimum_change_sample_2(self):
        """1.97 owed: 197 % 3 != 0 → minimum → "3 pennies"."""
        self.assertEqual(calculate_change("1.97", "2.00"), "3 pennies")

    def test_random_change_total_correct(self):
        """3.33 owed: 333 % 3 == 0 → random, change = 167 cents."""
        for _ in range(20):
            result = calculate_change("3.33", "5.00")
            self.assertEqual(parse_change_string(result), 167)

    def test_exact_payment_returns_empty(self):
        self.assertEqual(calculate_change("1.00", "1.00"), "")

    def test_underpayment_raises(self):
        with self.assertRaises(ValueError):
            calculate_change("5.00", "3.00")

    def test_random_divisor_constant_is_3(self):
        self.assertEqual(RANDOM_DIVISOR, 3)


class TestProcessLines(unittest.TestCase):
    def test_sample_input(self):
        lines = ["2.12,3.00\n", "1.97,2.00\n", "3.33,5.00\n"]
        results = process_lines(lines)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], "3 quarters,1 dime,3 pennies")
        self.assertEqual(results[1], "3 pennies")
        self.assertEqual(parse_change_string(results[2]), 167)  # third result is random; verify the total

    def test_blank_lines_are_ignored(self):
        lines = ["2.12,3.00\n", "\n", "1.97,2.00\n"]
        results = process_lines(lines)
        self.assertEqual(len(results), 2)

    def test_whitespace_around_values_tolerated(self):
        lines = [" 2.12 , 3.00 \n"]
        results = process_lines(lines)
        self.assertEqual(results[0], "3 quarters,1 dime,3 pennies")


if __name__ == "__main__":
    unittest.main()
