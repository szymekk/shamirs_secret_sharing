import unittest
from itertools import permutations

import shamir


class TestShamirSecretSharing(unittest.TestCase):

    def test_raises_value_error_on_k_greater_than_n(self):
        m = 2
        n = 5
        p = 7
        with self.assertRaises(ValueError):
            shamir.encode(message=m, k=n + 1, n=n, p=p)

    def test_raises_value_error_on_message_not_less_than_p(self):
        m = 3
        k = 3
        n = 3
        p = 3
        with self.assertRaises(ValueError):
            shamir.encode(message=m, k=k, n=n, p=p)

    def test_raises_value_error_on_n_greater_or_equal_p(self):
        m = 6
        k = 4
        p = 7
        with self.assertRaises(ValueError):
            shamir.encode(message=m, k=k, n=p, p=p)
        with self.assertRaises(ValueError):
            shamir.encode(message=m, k=k, n=p + 1, p=p)

    def test_decoded_equals_original_message(self):
        message = 10
        k = 10
        n = 11
        p = 13

        shares = shamir.encode(message=message, k=k, n=n, p=p)
        decoded = shamir.decode(shares=shares, k=k, p=p)
        self.assertEqual(message, decoded)

    def test_different_permutations_of_shares_give_the_same_result(self):
        message = 10
        k = 3
        n = 4
        p = 13

        shares = shamir.encode(message=message, k=k, n=n, p=p)
        for permutation in permutations(shares):
            decoded = shamir.decode(shares=permutation, k=k, p=p)
            self.assertEqual(message, decoded)


if __name__ == '__main__':
    unittest.main()
