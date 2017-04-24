import unittest

from asyncmqtt.util import *


class UtilTests(unittest.TestCase):
    def test_int_marshal_demarshal_tiny(self):
        value = 128
        as_bytes = int_to_bytes(value, 1)

        value2 = bytes_to_int(as_bytes)

        self.assertEqual(value, value2)

    def test_int_marshal_demarshal_small(self):
        value = 65535
        as_bytes = int_to_bytes(value, 2)

        value2 = bytes_to_int(as_bytes)

        self.assertEqual(value, value2)

    def test_int_marshal_demarshal_large(self):
        value = 1024768
        as_bytes = int_to_bytes(value, 3)

        value2 = bytes_to_int(as_bytes)

        self.assertEqual(value, value2)

    def test_int_marshal_demarshal_huge(self):
        value = 102476800
        as_bytes = int_to_bytes(value, 4)

        value2 = bytes_to_int(as_bytes)

        self.assertEqual(value, value2)

    def test_string_marshal_demarshal(self):
        basestr = 'hello world!'

        for multiplier in range(1, 8):
            encstr = basestr * (1 << multiplier)
            encstrb = encode_string(encstr)
            decstrb = decode_string(encstrb)

            self.assertEqual(encstr, decstrb)
