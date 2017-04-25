import unittest
from asyncmqtt.packet_connect import ConnectPacket


class ConnectPacketTests(unittest.TestCase):
    def test_marshal_demarshal(self):
        cp = ConnectPacket()
        cp.username = 'abc'
        cp.password = 'def'
        cp_bytes = cp.to_bytes()

        cp2 = ConnectPacket.from_bytes(cp_bytes)

        self.assertEqual(cp.username, cp2.username)
        self.assertEqual(cp.password, cp2.password)
