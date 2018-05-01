import random
from typing import List, Tuple, Set


def polyval_mod(coeffs: List[int], x: int, p: int) -> int:
    """Return the value of a polynomial over a finite field.
    coeffs is a list of coefficients of the polynomial
    p is the order of the field
    len(coeffs) = k
    coeffs = [a_k-1, ... a_1, a_0]
    polyval(coeffs, x, p) = (a_k-1 * x ** k-1 + ... + a_1 * x + a_0) % p
    """

    acc = 0
    for a in coeffs:
        acc *= x
        acc += a
        acc %= p
    return acc


Point = Tuple[int, int]


def random_sample_range(a: int, b: int, k: int) -> List[int]:
    """Sample k elements without replacements from integer range [a, b].
    Similar to random.sample(range(a, b + 1), k), but handles large ranges.
    """

    if b - a + 1 < k:
        raise ValueError('Requested sample size is larger than population.')

    sampled: Set[int] = set()
    for i in range(k):
        r = random.randint(a, b)
        while r in sampled:
            r = random.randint(a, b)
        sampled.add(r)
    return list(sampled)


def encode(message: int, k: int, n: int, p: int) -> List[Point]:
    """message - number to be encoded into shares
    k - minimal number of shares to recover the message
    n - total number of shares
    p - field size
    """
    if k < 1:
        raise ValueError("Minimal number of chunks must be at least one.")
    if n < k:
        raise ValueError("Minimal number of chunks cannot exceed total chunk count.")
    if p <= message:
        raise ValueError("Message must be smaller than the field size.")
    if p <= n:
        raise ValueError("Total chunk count must be smaller than the field size.")

    # get n unique field elements
    # skip 0 because the corresponding share: (0, f(0))
    # contains the secret: f(0) == message
    # random.sample doesn't work with large ranges
    # xs = random.sample(range(1, p), n)
    xs = random_sample_range(1, p - 1, n)
    coeffs = [random.randint(0, p - 1) for _ in range(k)]
    coeffs[-1] = message
    ys = [polyval_mod(coeffs, x, p) for x in xs]
    assert polyval_mod(coeffs, 0, p) == message
    points = list(zip(xs, ys))
    return points


def decode(shares: List[Point], k: int, p: int) -> int:
    """shares - list of points
    k - minimal number of shares to recover the message
    p - field size
    """
    if k >= p:
        raise ValueError("Minimal number of chunks must be smaller than the field size.")
    if k > len(shares):
        raise ValueError("To few shares to recover the secret.")
    all_numerator_product = 1
    k_shares = shares[:k]
    for x, y in k_shares:
        all_numerator_product *= x

    # if p is prime than the multiplicative inverse of a can be calculated using Euler's theorem
    # a ** totient(p) = 1 (mod p)
    # a ** (totient(p) - 1) = a ** -1 (mod p)
    # for prime p totient(p) == p-1
    # a ** -1 == a ** (p - 2)
    # TODO calculate using extended euclidean algorithm (extended greatest common divisor)
    # current implementation only works for prime p
    def inv(val):
        return pow(val, p - 2, p)

    def lagrange_at_zero_times_y(j):
        """Compute y_j * l_j(0) where l_j is the j-th lagrange polynomial."""
        x_j, y_j = k_shares[j]
        denominator_product = 1
        for i, (x, y) in enumerate(k_shares):
            if j != i:
                denominator_product *= (x - x_j)

        x_j_inv = inv(x_j)
        assert (x_j_inv * x_j % p) == 1, 'inv is not an inverse'
        numerator_product = all_numerator_product * x_j_inv
        product = (inv(denominator_product) * numerator_product) % p
        return (y_j * product) % p

    acc = 0
    for i in range(k):
        acc += lagrange_at_zero_times_y(i)
    return acc % p


def str_to_int(string: str) -> int:
    string_as_bytes = string.encode()
    string_as_int = int.from_bytes(string_as_bytes, byteorder='big')
    return string_as_int


def int_to_str(integer: int) -> str:
    integer_as_bytes = integer.to_bytes((integer.bit_length() + 7) // 8, 'big')
    integer_as_str = integer_as_bytes.decode()
    return integer_as_str
