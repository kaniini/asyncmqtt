import unittest

from asyncmqtt.packet_ping import PingReqPacket, PingRespPacket


class PingReqPacketTests(unittest.TestCase):
    def test_marshal_demarshal(self):
        p1 = PingReqPacket()
        p1_bytes = p1.to_bytes()

        p2 = PingReqPacket.from_bytes(p1_bytes)
        self.assertEqual(p1_bytes, p2.to_bytes())


class PingRespPacketTests(unittest.TestCase):
    def test_marshal_demarshal(self):
        p1 = PingRespPacket()
        p1_bytes = p1.to_bytes()

        p2 = PingRespPacket.from_bytes(p1_bytes)
        self.assertEqual(p1_bytes, p2.to_bytes())

