import unittest

from asyncmqtt.packet import CONNECT, MQTTFixedHeader


class MQTTFixedHeaderTests(unittest.TestCase):
    def test_marshal_demarshal_tiny(self):
        fh1 = MQTTFixedHeader(CONNECT, 0, 128)
        fh1_bytes = fh1.to_bytes()

        fh2 = MQTTFixedHeader.from_bytes(fh1_bytes)
        self.assertEqual(fh1.remaining_length, fh2.remaining_length)
        self.assertEqual(fh1_bytes, fh2.to_bytes())

    def test_marshal_demarshal_small(self):
        fh1 = MQTTFixedHeader(CONNECT, 0, 65536)
        fh1_bytes = fh1.to_bytes()

        fh2 = MQTTFixedHeader.from_bytes(fh1_bytes)
        self.assertEqual(fh1.remaining_length, fh2.remaining_length)
        self.assertEqual(fh1_bytes, fh2.to_bytes())

    def test_marshal_demarshal_large(self):
        fh1 = MQTTFixedHeader(CONNECT, 0, 1024768)
        fh1_bytes = fh1.to_bytes()

        fh2 = MQTTFixedHeader.from_bytes(fh1_bytes)
        self.assertEqual(fh1.remaining_length, fh2.remaining_length)
        self.assertEqual(fh1_bytes, fh2.to_bytes())

    def test_marshal_demarshal_huge(self):
        fh1 = MQTTFixedHeader(CONNECT, 0, 102476800)
        fh1_bytes = fh1.to_bytes()

        fh2 = MQTTFixedHeader.from_bytes(fh1_bytes)
        self.assertEqual(fh1.remaining_length, fh2.remaining_length)
        self.assertEqual(fh1_bytes, fh2.to_bytes())

    @unittest.expectedFailure
    def test_marshal_demarshal_truncated(self):
        fh1 = MQTTFixedHeader(CONNECT, 0, 102476800)
        fh1_bytes = fh1.to_bytes()[:-1]

        fh2 = MQTTFixedHeader.from_bytes(fh1_bytes)
