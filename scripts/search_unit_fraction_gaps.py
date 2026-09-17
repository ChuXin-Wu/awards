#!/usr/bin/env python3
"""Search bounded cases of JSP-000244 / Erdős problem 287 exactly.

A counterexample of length k would be a sequence

    1 < n_1 < ... < n_k,  sum(1 / n_i) = 1,

whose consecutive gaps are all 1 or 2.  Such a sequence is determined by
``n_1`` and a binary gap pattern.  It is enough to test ``2 <= n_1 < k``:
when ``n_1 >= k``, every term is at most ``1 / n_1`` and at least one is
strictly smaller, so the reciprocal sum is less than 1.

The search uses exact ``Fraction`` arithmetic, rigorous upper/lower tail
bounds, and a p-adic obstruction to integer reciprocal sums.  A negative
result proves the conjecture only for the requested finite range of lengths.
"""

import argparse
import json
from fractions import Fraction
from functools import lru_cache
from typing import Dict, List, Optional, Tuple


@lru_cache(maxsize=None)
def tail_sum(current: int, remaining: int, gap: int) -> Fraction:
    return sum(
        (Fraction(1, current + gap * offset) for offset in range(1, remaining + 1)),
        Fraction(0),
    )


@lru_cache(maxsize=None)
def prime_power_factors(value: int) -> Tuple[Tuple[int, int], ...]:
    """Return ``(prime, maximal prime power)`` pairs dividing ``value``."""
    factors = []
    remainder = value
    prime = 2
    while prime * prime <= remainder:
        if remainder % prime == 0:
            power = 1
            while remainder % prime == 0:
                remainder //= prime
                power *= prime
            factors.append((prime, power))
        prime += 1
    if remainder > 1:
        factors.append((remainder, remainder))
    return tuple(factors)


def has_stranded_prime_power(sequence: List[int], remaining: int) -> bool:
    """Detect a prime power that cannot attain its maximum twice.

    If reciprocals of the completed denominator sequence sum to an integer,
    the largest p-adic valuation among its denominators cannot occur exactly
    once.  This function returns true when a current unique maximum has no
    possible future multiple in the broadest reachable denominator interval.
    """
    maxima: Dict[int, Tuple[int, int]] = {}
    for denominator in sequence:
        for prime, power in prime_power_factors(denominator):
            previous = maxima.get(prime)
            if previous is None or power > previous[0]:
                maxima[prime] = (power, 1)
            elif power == previous[0]:
                maxima[prime] = (power, previous[1] + 1)

    current = sequence[-1]
    largest_reachable = current + 2 * remaining
    for power, count in maxima.values():
        if count != 1:
            continue
        next_multiple = (current // power + 1) * power
        if next_multiple > largest_reachable:
            return True
    return False


def search_length(length: int) -> Dict[str, object]:
    if length < 2:
        raise ValueError("length must be at least 2")

    nodes = 0
    pruned_below = 0
    pruned_above = 0
    pruned_prime_power = 0

    def visit(sequence: List[int], total: Fraction) -> Optional[List[int]]:
        nonlocal nodes, pruned_above, pruned_below, pruned_prime_power
        nodes += 1
        remaining = length - len(sequence)
        if has_stranded_prime_power(sequence, remaining):
            pruned_prime_power += 1
            return None
        if remaining == 0:
            return sequence.copy() if total == 1 else None
        if total >= 1:
            pruned_above += 1
            return None

        current = sequence[-1]
        # Gap 1 maximises the remaining sum; gap 2 minimises it.
        if total + tail_sum(current, remaining, 1) < 1:
            pruned_below += 1
            return None
        if total + tail_sum(current, remaining, 2) > 1:
            pruned_above += 1
            return None

        for gap in (1, 2):
            denominator = current + gap
            sequence.append(denominator)
            witness = visit(sequence, total + Fraction(1, denominator))
            sequence.pop()
            if witness is not None:
                return witness
        return None

    for first in range(2, length):
        witness = visit([first], Fraction(1, first))
        if witness is not None:
            return {
                "length": length,
                "witness": witness,
                "nodes": nodes,
                "pruned_above": pruned_above,
                "pruned_below": pruned_below,
                "pruned_prime_power": pruned_prime_power,
            }

    return {
        "length": length,
        "witness": None,
        "nodes": nodes,
        "pruned_above": pruned_above,
        "pruned_below": pruned_below,
        "pruned_prime_power": pruned_prime_power,
    }


def scan(max_length: int) -> Dict[str, object]:
    if max_length < 2:
        raise ValueError("max_length must be at least 2")
    results = []
    for length in range(2, max_length + 1):
        result = search_length(length)
        results.append(result)
        if result["witness"] is not None:
            break
    return {"max_length": max_length, "results": results}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--length", type=int, help="check one length only")
    group.add_argument("--max-length", type=int, default=18)
    args = parser.parse_args()
    result = search_length(args.length) if args.length is not None else scan(args.max_length)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
