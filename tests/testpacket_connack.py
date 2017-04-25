import unittest
from asyncmqtt.packet_connack import ConnackPacket


class ConnAckPacketTests(unittest.TestCase):
    def test_marshal_demarshal(self):
        p1 = ConnackPacket.build(0)
        p1_bytes = p1.to_bytes()

        p2 = ConnackPacket.from_bytes(p1_bytes)
        self.assertEqual(p1.return_code, p2.return_code)
        self.assertEqual(p1_bytes, p2.to_bytes())
