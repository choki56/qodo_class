#!/usr/bin/env python3

import math


def is_prime(n: int) -> bool:
    """Return True if n is a prime number, else False."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    limit = int(math.sqrt(n))
    for i in range(3, limit + 1, 2):
        if n % i == 0:
            return False
    return True


def primes_up_to(limit: int):
    """Generate all prime numbers from 2 up to 'limit' inclusive."""
    return [n for n in range(2, limit + 1) if is_prime(n)]


def is_even(n: int) -> bool:
    """Return True if n is even, else False."""
    return n % 2 == 0


if __name__ == "__main__":
    primes = primes_up_to(100)
    print(" ".join(map(str, primes)))
