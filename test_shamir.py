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

    def test_decode_raises_value_error_on_empty_shares(self):
        k = 3
        p = 13
        with self.assertRaises(ValueError):
            shamir.decode([], k=k, p=p)


class TestStringSharing(unittest.TestCase):
    def test_str_to_int_returns_int(self):
        string = 'abc'
        integer = shamir.str_to_int(string)
        self.assertIsInstance(integer, int)

    def test_int_to_str_returns_str(self):
        integer = 5
        string = shamir.int_to_str(integer)
        self.assertIsInstance(string, str)

    def test_str_to_int_and_back(self):
        string = 'abc'
        integer = shamir.str_to_int(string)
        recovered_string = shamir.int_to_str(integer)
        self.assertEqual(string, recovered_string)

    def test_int_to_str_and_back(self):
        integer = 13
        string = shamir.int_to_str(integer)
        recovered_integer = shamir.str_to_int(string)
        self.assertEqual(integer, recovered_integer)

    def test_decoded_str_equals_original(self):
        k = 3
        n = 5
        p = 2 ** 61 - 1  # 9th Mersenne prime
        string = 'message'
        integer = shamir.str_to_int(string)
        shares = shamir.encode(integer, k=k, n=n, p=p)
        recovered_integer = shamir.decode(shares, k=k, p=p)
        recovered_string = shamir.int_to_str(recovered_integer)
        self.assertEqual(string, recovered_string)

    def test_encoding_large_strings(self):
        k = 3
        n = 5
        p = 2 ** 521 - 1  # 13th Mersenne prime
        string = 'This is a pretty long secret message. Big field order is needed.'
        integer = shamir.str_to_int(string)
        shares = shamir.encode(integer, k=k, n=n, p=p)
        recovered_integer = shamir.decode(shares, k=k, p=p)
        recovered_string = shamir.int_to_str(recovered_integer)
        self.assertEqual(string, recovered_string)


if __name__ == '__main__':
    unittest.main()
