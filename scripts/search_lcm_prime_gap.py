#!/usr/bin/env python3
"""Search for a finite counterexample to JSP-000372 / Erdős problem 458.

For consecutive primes p_k < p_{k+1}, let L(n) = lcm(1, ..., n).  The
question is whether

    L(p_{k+1} - 1) < p_k * L(p_k)

always holds.  The quotient on the left changes only when the interval
(p_k, p_{k+1}) contains a prime power q**a (a >= 2).  Crossing q**a
multiplies the quotient by q.  Consequently a counterexample is exactly a
prime gap for which the product of those bases q is at least p_k.

This script performs that reduced exact-integer check.  A run with limit N
checks every consecutive-prime pair whose right endpoint is at most N.
Absence of a counterexample is computational evidence, not a proof.
"""

import argparse
import json
import math
from typing import Dict, Iterator, List, Tuple


def odd_prime_sieve(limit: int) -> bytearray:
    """Return an odd-only primality table for integers at most ``limit``."""
    size = limit // 2 + 1
    sieve = bytearray(b"\x01") * size
    if size:
        sieve[0] = 0  # 1 is not prime.
    root = math.isqrt(limit)
    for prime in range(3, root + 1, 2):
        if not sieve[prime // 2]:
            continue
        start = prime * prime // 2
        count = (size - 1 - start) // prime + 1
        sieve[start::prime] = b"\x00" * count
    return sieve


def iter_primes(sieve: bytearray, limit: int) -> Iterator[int]:
    if limit >= 2:
        yield 2
    for index in range(1, len(sieve)):
        value = 2 * index + 1
        if value > limit:
            break
        if sieve[index]:
            yield value


def prime_power_events(limit: int) -> List[Tuple[int, int]]:
    """Return ``(q**a, q)`` for prime q and a >= 2, up to ``limit``."""
    base_limit = math.isqrt(limit)
    base_sieve = odd_prime_sieve(base_limit)
    events: List[Tuple[int, int]] = []
    for base in iter_primes(base_sieve, base_limit):
        power = base * base
        while power <= limit:
            events.append((power, base))
            if power > limit // base:
                break
            power *= base
    events.sort()
    return events


def scan(limit: int) -> Dict[str, object]:
    if limit < 3:
        raise ValueError("limit must be at least 3")

    sieve = odd_prime_sieve(limit)
    events = prime_power_events(limit)
    event_index = 0
    previous = None
    checked = 0
    nonempty_gaps = 0
    closest = None

    for current in iter_primes(sieve, limit):
        if previous is None:
            previous = current
            continue

        while event_index < len(events) and events[event_index][0] <= previous:
            event_index += 1
        cursor = event_index
        quotient = 1
        gap_events = []
        while cursor < len(events) and events[cursor][0] < current:
            power, base = events[cursor]
            quotient *= base
            gap_events.append({"power": power, "base": base})
            cursor += 1

        checked += 1
        if gap_events:
            nonempty_gaps += 1
            if closest is None or quotient * closest["left_prime"] > closest["quotient"] * previous:
                closest = {
                    "left_prime": previous,
                    "right_prime": current,
                    "quotient": quotient,
                    "prime_powers": gap_events,
                }
        if quotient >= previous:
            return {
                "counterexample": {
                    "left_prime": previous,
                    "right_prime": current,
                    "quotient": quotient,
                    "prime_powers": gap_events,
                },
                "checked_prime_gaps": checked,
                "limit": limit,
            }

        previous = current

    return {
        "counterexample": None,
        "checked_prime_gaps": checked,
        "nonempty_prime_power_gaps": nonempty_gaps,
        "largest_checked_prime": previous,
        "closest_case": closest,
        "limit": limit,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=10_000_000)
    args = parser.parse_args()
    print(json.dumps(scan(args.limit), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
