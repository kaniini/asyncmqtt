import unittest
from asyncmqtt.packet_suback import SubackPacket


class SubackPacketTests(unittest.TestCase):
    def test_marshal_demarshal(self):
        sp = SubackPacket.build(0, [0x0, 0x1, 0x2])
        sp_bytes = sp.to_bytes()

        sp2 = SubackPacket.from_bytes(sp_bytes)
        self.assertEqual(sp.return_codes, sp2.return_codes)
        self.assertEqual(sp_bytes, sp2.to_bytes())
