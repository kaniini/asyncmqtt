import unittest
from asyncmqtt.packet_publish import PublishPacket


class PublishPacketTests(unittest.TestCase):
    def test_marshal_demarshal(self):
        pp = PublishPacket.build('moo', b'cows go moo', None, False, False, False)
        pp_bytes = pp.to_bytes()

        pp2 = PublishPacket.from_bytes(pp_bytes)
        self.assertEqual(pp.topic_name, pp2.topic_name)
        self.assertEqual(pp.data, pp2.data)
        self.assertEqual(pp_bytes, pp2.to_bytes())

    def test_marshal_demarshal_qos(self):
        pp = PublishPacket.build('moo', b'cows go moo', 0xffff, False, True, False)
        pp_bytes = pp.to_bytes()

        pp2 = PublishPacket.from_bytes(pp_bytes)
        self.assertEqual(pp.topic_name, pp2.topic_name)
        self.assertEqual(pp.data, pp2.data)
        self.assertEqual(pp_bytes, pp2.to_bytes())

    @unittest.expectedFailure
    def test_marshal_demarshal_packetid_without_qos(self):
        pp = PublishPacket.build('moo', b'cows go moo', 0xffff, False, False, False)
        pp_bytes = pp.to_bytes()

        pp2 = PublishPacket.from_bytes(pp_bytes)
        self.assertEqual(pp.topic_name, pp2.topic_name)
        self.assertEqual(pp.data, pp2.data)
        self.assertEqual(pp_bytes, pp2.to_bytes())
