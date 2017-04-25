import unittest
from asyncmqtt.packet_subscribe import SubscribePacket


class SubscribePacketTests(unittest.TestCase):
    def test_marshal_demarshal(self):
        sp = SubscribePacket.build([('#', 1)], 0)
        sp_bytes = sp.to_bytes()

        sp2 = SubscribePacket.from_bytes(sp_bytes)
        self.assertEqual(sp.topics, sp2.topics)
        self.assertEqual(sp_bytes, sp2.to_bytes())
