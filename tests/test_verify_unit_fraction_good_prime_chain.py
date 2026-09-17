"""Tests for the JSP-000244 good-prime-chain certificate."""

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_unit_fraction_good_prime_chain as certificate  # noqa: E402


class GoodPrimeChainCertificateTests(unittest.TestCase):
    def test_deterministic_64_bit_primality(self):
        self.assertTrue(certificate.is_prime_below_2_64(18446744073709551557))
        self.assertFalse(certificate.is_prime_below_2_64(18446744073709551555))

    def test_recursive_pocklington_certificates(self):
        memo = {}
        for value in certificate.POCKLINGTON_CERTIFICATES:
            self.assertTrue(certificate.prove_prime(value, memo))

        largest = max(certificate.POCKLINGTON_CERTIFICATES)
        tampered = dict(certificate.POCKLINGTON_CERTIFICATES)
        factor, _ = tampered[largest]
        tampered[largest] = (factor, 1)
        self.assertFalse(certificate.prove_prime(largest, {}, tampered))

    def test_broken_chain_is_rejected(self):
        with self.assertRaises(AssertionError):
            certificate.verify_chain((13, 37))

    def test_full_certificate(self):
        result = certificate.verify_certificate()
        self.assertEqual(result["coverage_first_M"], 14)
        self.assertEqual(result["coverage_last_M"], 295147905179333672635)
        self.assertEqual(
            result["first_denominator_must_exceed"],
            certificate.EXPECTED_FIRST_DENOMINATOR_FLOOR,
        )
        self.assertEqual(
            result["length_must_be_at_least"],
            certificate.EXPECTED_LENGTH_LOWER_BOUND,
        )


if __name__ == "__main__":
    unittest.main()
