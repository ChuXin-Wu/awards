"""Tests for the bounded exact search for JSP-000244."""

import sys
import unittest
from fractions import Fraction
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import search_unit_fraction_gaps as search  # noqa: E402


class UnitFractionGapSearchTests(unittest.TestCase):
    def test_tail_sum(self):
        self.assertEqual(search.tail_sum(2, 2, 2), Fraction(5, 12))

    def test_stranded_prime_power_obstruction(self):
        self.assertTrue(search.has_stranded_prime_power([5, 6, 7], 0))
        self.assertFalse(search.has_stranded_prime_power([2, 3, 6], 0))

    def test_full_top_layer_congruence_is_checked(self):
        # The maximum 31-adic valuation occurs twice, so a unique-maximum
        # test cannot reject this sequence.  Its required top-layer sum is
        # 1 + 1/2, which is nonzero modulo 31.
        sequence = [
            9, 11, 13, 14, 16, 17, 19, 21, 23, 25,
            27, 29, 31, 33, 34, 36, 38, 40, 42, 44,
            46, 48, 50, 52, 54, 56, 58, 60, 62,
        ]
        self.assertTrue(search.has_stranded_prime_power(sequence, 0))

    def test_lower_p_adic_layers_are_retained(self):
        layers = {}
        prefix = []
        for denominator in [2, 4, 12]:
            prefix.append(denominator)
            layers = search.extend_top_layers(layers, prefix)
        # The two top-layer cofactors 1 and 3 cancel modulo 2, but the
        # denominator 2 contributes a carry: 1 + 3 + 2 = 2 (mod 4).
        self.assertEqual(layers[2], (4, 2))
        self.assertTrue(search.has_impossible_top_layer(layers, 12, 0))

    def test_no_counterexample_through_ten_terms(self):
        result = search.scan(10)
        self.assertEqual(len(result["results"]), 9)
        self.assertTrue(all(item["witness"] is None for item in result["results"]))

    def test_pruned_search_matches_independent_exhaustion(self):
        for length in range(2, 11):
            brute_witness = None
            for first in range(2, length):
                for gaps in product((1, 2), repeat=length - 1):
                    sequence = [first]
                    for gap in gaps:
                        sequence.append(sequence[-1] + gap)
                    total = sum((Fraction(1, n) for n in sequence), Fraction(0))
                    if total == 1:
                        brute_witness = sequence
                        break
                if brute_witness is not None:
                    break
            self.assertEqual(search.search_length(length)["witness"], brute_witness)

    def test_reported_witness_would_be_checked_exactly(self):
        # This is not a counterexample; it checks the exact verifier predicate.
        sequence = [2, 3, 6]
        self.assertEqual(sum((Fraction(1, n) for n in sequence), Fraction(0)), 1)
        self.assertEqual(max(b - a for a, b in zip(sequence, sequence[1:])), 3)


if __name__ == "__main__":
    unittest.main()
