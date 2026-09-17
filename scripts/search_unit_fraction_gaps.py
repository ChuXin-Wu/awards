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
from typing import Dict, FrozenSet, List, Optional, Tuple


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


TopLayers = Dict[int, Tuple[int, int]]


def prime_power_dividing(value: int, prime: int) -> int:
    """Return the largest power of ``prime`` dividing ``value``."""
    power = 1
    while value % prime == 0:
        value //= prime
        power *= prime
    return power


def extend_top_layers(layers: TopLayers, sequence: List[int]) -> TopLayers:
    """Return maximal p-powers and full normalized p-adic residues."""
    denominator = sequence[-1]
    extended = layers.copy()
    for prime, power in prime_power_factors(denominator):
        previous = extended.get(prime)
        if previous is None:
            extended[prime] = (
                power,
                pow(denominator // power, -1, power),
            )
        elif power > previous[0]:
            residue = 0
            for selected in sequence:
                if selected % prime != 0:
                    continue
                selected_power = prime_power_dividing(selected, prime)
                residue += (power // selected_power) * pow(
                    selected // selected_power, -1, power
                )
            extended[prime] = (power, residue % power)
        else:
            modulus = previous[0]
            addend = (modulus // power) * pow(
                denominator // power, -1, modulus
            )
            extended[prime] = (
                modulus,
                (previous[1] + addend) % modulus,
            )
    return extended


@lru_cache(maxsize=None)
def reachable_top_layer_residues(
    prime: int, power: int, current: int, largest_reachable: int
) -> Optional[FrozenSet[int]]:
    """Over-approximate normalized p-adic residues from future p-multiples.

    ``None`` means that the residue set exceeded the deliberately modest cap,
    so callers must keep the branch.
    """
    residues = {0}
    first_multiple = ((current // prime) + 1) * prime
    for denominator in range(first_multiple, largest_reachable + 1, prime):
        denominator_power = prime_power_dividing(denominator, prime)
        addend = (power // denominator_power) * pow(
            denominator // denominator_power, -1, power
        )
        residues |= {(candidate + addend) % power for candidate in residues}
        if len(residues) == power:
            break
        if len(residues) > 4096:
            return None
    return frozenset(residues)


def has_impossible_top_layer(
    layers: TopLayers, current: int, remaining: int
) -> bool:
    """Test whether some fixed maximal p-power cannot cancel modulo that power."""
    largest_reachable = current + 2 * remaining
    for prime, (power, residue) in layers.items():
        # A higher p-adic layer could replace the current one.
        next_higher = ((current // (power * prime)) + 1) * power * prime
        if next_higher <= largest_reachable:
            continue

        possible_residues = reachable_top_layer_residues(
            prime, power, current, largest_reachable
        )
        if (
            possible_residues is not None
            and (-residue) % power not in possible_residues
        ):
            return True
    return False


def has_stranded_prime_power(sequence: List[int], remaining: int) -> bool:
    """Detect a normalized p-adic residue that no future subset can cancel.

    If reciprocals of the completed denominator sequence sum to an integer,
    then, for every prime ``p`` with maximal selected p-power ``p**e``, the
    normalized contributions from every positive p-adic layer must sum to zero
    modulo ``p**e``. Future values are deliberately allowed to be an arbitrary
    subset of the broadest reachable interval, ignoring the gap and
    remaining-length constraints. Thus a failed modular subset-sum test is a
    sound obstruction.

    If a future value can be divisible by a still higher power of ``p``, the
    current top layer may cease to be relevant and the test conservatively
    declines to prune.  Very large residue sets are likewise skipped; that
    affects speed only, never correctness.
    """
    layers: TopLayers = {}
    prefix: List[int] = []
    for denominator in sequence:
        prefix.append(denominator)
        layers = extend_top_layers(layers, prefix)
    return has_impossible_top_layer(layers, sequence[-1], remaining)


def search_length(length: int) -> Dict[str, object]:
    if length < 2:
        raise ValueError("length must be at least 2")

    nodes = 0
    pruned_below = 0
    pruned_above = 0
    pruned_prime_power = 0

    def visit(
        sequence: List[int], total: Fraction, layers: TopLayers
    ) -> Optional[List[int]]:
        nonlocal nodes, pruned_above, pruned_below, pruned_prime_power
        nodes += 1
        remaining = length - len(sequence)
        if has_impossible_top_layer(layers, sequence[-1], remaining):
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
            witness = visit(
                sequence,
                total + Fraction(1, denominator),
                extend_top_layers(layers, sequence),
            )
            sequence.pop()
            if witness is not None:
                return witness
        return None

    for first in range(2, length):
        witness = visit(
            [first], Fraction(1, first), extend_top_layers({}, [first])
        )
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
