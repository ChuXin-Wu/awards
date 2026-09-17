#!/usr/bin/env python3
"""Verify the finite good-prime-chain certificate for JSP-000244.

The certificate does not settle Erdős problem 287.  It proves that a
counterexample, if one exists, must start with an extremely large denominator.
All integer comparisons and the bounds for ``e`` and ``e**2`` are checked with
exact rational arithmetic.

Primality below 2**64 is checked with the deterministic seven-base
Miller--Rabin test.  The six larger primes used by the certificate are proved
recursively with Pocklington's theorem; their terminal prime factors are below
2**64.
"""

import argparse
import json
from fractions import Fraction
from math import factorial, gcd
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple


GOOD_PRIME_CHAIN: Tuple[int, ...] = (
    13,
    23,
    37,
    61,
    107,
    193,
    383,
    757,
    1487,
    2963,
    5879,
    11701,
    23399,
    46679,
    93287,
    186481,
    372901,
    745753,
    1491493,
    2982899,
    5965643,
    11930987,
    23861687,
    47723279,
    95446487,
    190892903,
    381785617,
    763571173,
    1527142237,
    3054283703,
    6108566567,
    12217132813,
    24434264783,
    48868528993,
    97737057793,
    195474115453,
    390948230557,
    781896460979,
    1563792921721,
    3127585843007,
    6255171685921,
    12510343371563,
    25020686743033,
    50041373485547,
    100082746969523,
    200165493939001,
    400330987877123,
    800661975753803,
    1601323951507417,
    3202647903014447,
    6405295806027973,
    12810591612055513,
    25621183224110701,
    51242366448219263,
    102484732896437053,
    204969465792873143,
    409938931585745593,
    819877863171490597,
    1639755726342979307,
    3279511452685958219,
    6559022905371915361,
    13118045810743829821,
    18446744073709550147,
    36893488147419100019,
    73786976294837987927,
    147573952589666836319,
)


# Each entry is n: (q, a).  It certifies n by Pocklington using the known
# prime divisor q of n - 1 and witness a.  In every case n - 1 = 2q, so
# q > sqrt(n).  Some q are themselves certified recursively here.
POCKLINGTON_CERTIFICATES: Mapping[int, Tuple[int, int]] = {
    36893488147419100019: (18446744073709550009, 2),
    36893488147418993963: (18446744073709496981, 2),
    73786976294837987927: (36893488147418993963, 2),
    36893488147416709079: (18446744073708354539, 2),
    73786976294833418159: (36893488147416709079, 2),
    147573952589666836319: (73786976294833418159, 2),
}


TWO_TO_64 = 1 << 64
MILLER_RABIN_BASES_64 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
EXPECTED_FIRST_DENOMINATOR_FLOOR = 39943925344138028689
EXPECTED_LENGTH_LOWER_BOUND = 68634921076157089631


def is_prime_below_2_64(value: int) -> bool:
    """Return primality for ``value < 2**64`` by deterministic Miller--Rabin."""
    if not 0 <= value < TWO_TO_64:
        raise ValueError("the deterministic test is restricted to [0, 2**64)")
    if value < 2:
        return False
    for prime in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if value % prime == 0:
            return value == prime

    odd_part = value - 1
    power_of_two = 0
    while odd_part % 2 == 0:
        power_of_two += 1
        odd_part //= 2

    for base in MILLER_RABIN_BASES_64:
        base %= value
        if base == 0:
            continue
        residue = pow(base, odd_part, value)
        if residue in (1, value - 1):
            continue
        for _ in range(power_of_two - 1):
            residue = residue * residue % value
            if residue == value - 1:
                break
        else:
            return False
    return True


def prove_prime(
    value: int,
    memo: Optional[MutableMapping[int, bool]] = None,
    certificates: Mapping[int, Tuple[int, int]] = POCKLINGTON_CERTIFICATES,
) -> bool:
    """Verify primality using the 64-bit test or a recursive Pocklington proof."""
    if memo is None:
        memo = {}
    if value in memo:
        return memo[value]
    if value < TWO_TO_64:
        result = is_prime_below_2_64(value)
        memo[value] = result
        return result
    if value not in certificates:
        memo[value] = False
        return False

    prime_factor, witness = certificates[value]
    result = (
        (value - 1) % prime_factor == 0
        and prime_factor * prime_factor > value
        and prove_prime(prime_factor, memo, certificates)
        and pow(witness, value - 1, value) == 1
        and gcd(pow(witness, (value - 1) // prime_factor, value) - 1, value) == 1
    )
    memo[value] = result
    return result


def prime_half(value: int, memo: MutableMapping[int, bool]) -> int:
    """Return a prime among (value - 1)/2 and (value + 1)/2, or raise."""
    for candidate in ((value - 1) // 2, (value + 1) // 2):
        if prove_prime(candidate, memo):
            return candidate
    raise AssertionError(f"{value} has no prime half-neighbour")


def verify_chain(chain: Iterable[int] = GOOD_PRIME_CHAIN) -> Dict[str, object]:
    """Verify primality, goodness, and overlap of every coverage interval."""
    values = tuple(chain)
    if not values:
        raise AssertionError("the chain is empty")
    memo: Dict[int, bool] = {}
    halves: List[int] = []
    for value in values:
        if not prove_prime(value, memo):
            raise AssertionError(f"chain entry is not certified prime: {value}")
        halves.append(prime_half(value, memo))

    for left, right in zip(values, values[1:]):
        if not left < right:
            raise AssertionError("chain entries are not strictly increasing")
        if right > 2 * left - 3:
            raise AssertionError(f"coverage gap after {left}: next entry is {right}")

    return {
        "chain_length": len(values),
        "first_prime": values[0],
        "last_prime": values[-1],
        "coverage_first_M": values[0] + 1,
        "coverage_last_M": 2 * values[-1] - 3,
        "prime_halves": halves,
    }


def exponential_bounds(terms: int = 30) -> Tuple[Fraction, Fraction]:
    """Return exact bounds ``e_lower < e`` and ``e**2 < e2_upper``.

    The lower bound is a partial series for exp(1).  For exp(2), after the
    term indexed by ``terms`` each successive term has ratio at most
    ``2 / (terms + 2)``; the omitted tail is therefore bounded by a geometric
    series.
    """
    if terms < 1:
        raise ValueError("terms must be positive")
    e_lower = sum(
        (Fraction(1, factorial(index)) for index in range(terms + 1)),
        Fraction(0),
    )
    e2_partial = sum(
        (Fraction(2**index, factorial(index)) for index in range(terms + 1)),
        Fraction(0),
    )
    first_omitted = Fraction(2 ** (terms + 1), factorial(terms + 1))
    maximum_ratio = Fraction(2, terms + 2)
    e2_upper = e2_partial + first_omitted / (1 - maximum_ratio)
    return e_lower, e2_upper


def finite_consequences(last_prime: int, terms: int = 30) -> Dict[str, int]:
    """Compute rigorous lower bounds implied by the verified chain.

    If the first denominator ``a`` were at most floor(2P/e**2), the harmonic
    lower bound would give ``M + 2 < e**2 a <= 2P``.  The chain would then
    cover the largest denominator M and rule out the representation.
    """
    e_lower, e2_upper = exponential_bounds(terms)
    first_denominator_floor = (
        2 * last_prime * e2_upper.denominator // e2_upper.numerator
    )
    scaled_length_bound = (e_lower - 1) * first_denominator_floor
    length_lower_bound = (
        scaled_length_bound.numerator // scaled_length_bound.denominator + 1
    )
    return {
        "first_denominator_must_exceed": first_denominator_floor,
        "length_must_be_at_least": length_lower_bound,
        "series_terms": terms,
    }


def verify_certificate() -> Dict[str, object]:
    chain_result = verify_chain()
    consequence = finite_consequences(int(chain_result["last_prime"]))
    if consequence["first_denominator_must_exceed"] != EXPECTED_FIRST_DENOMINATOR_FLOOR:
        raise AssertionError("unexpected first-denominator bound")
    if consequence["length_must_be_at_least"] != EXPECTED_LENGTH_LOWER_BOUND:
        raise AssertionError("unexpected length bound")
    return {**chain_result, **consequence}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(verify_certificate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
