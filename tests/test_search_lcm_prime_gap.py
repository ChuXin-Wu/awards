"""Checks for the exact reduction used by search_lcm_prime_gap.py."""

import math
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import search_lcm_prime_gap as search  # noqa: E402


class LcmPrimeGapSearchTests(unittest.TestCase):
    def test_prime_power_events(self):
        self.assertEqual(
            search.prime_power_events(30),
            [(4, 2), (8, 2), (9, 3), (16, 2), (25, 5), (27, 3)],
        )

    def test_reduced_quotients_match_direct_lcm_computation(self):
        limit = 10_000
        sieve = search.odd_prime_sieve(limit)
        primes = list(search.iter_primes(sieve, limit))
        events = search.prime_power_events(limit)

        lcm_value = 1
        lcms = [1] * (limit + 1)
        for value in range(1, limit + 1):
            lcm_value = lcm_value * value // math.gcd(lcm_value, value)
            lcms[value] = lcm_value

        for left, right in zip(primes, primes[1:]):
            reduced = 1
            for power, base in events:
                if left < power < right:
                    reduced *= base
            direct = lcms[right - 1] // lcms[left]
            self.assertEqual(reduced, direct, (left, right))

    def test_no_small_counterexample_and_known_closest_case(self):
        result = search.scan(1_000)
        self.assertIsNone(result["counterexample"])
        self.assertEqual(result["closest_case"]["left_prime"], 7)
        self.assertEqual(result["closest_case"]["right_prime"], 11)
        self.assertEqual(result["closest_case"]["quotient"], 6)


if __name__ == "__main__":
    unittest.main()
