import asyncio


from asyncmqtt import MQTTException
from asyncmqtt.util import bytes_as_hex
from asyncmqtt.packet import MQTTFixedHeader, CONNECT, CONNACK, PUBLISH, PUBACK, PUBREC, PUBREL, PUBCOMP, SUBSCRIBE, SUBACK, UNSUBSCRIBE, UNSUBACK, PINGREQ, PINGRESP, DISCONNECT
from asyncmqtt.packet_ping import PingReqPacket, PingRespPacket
from asyncmqtt.packet_connect import ConnectPacket
from asyncmqtt.packet_connack import ConnackPacket
from asyncmqtt.packet_subscribe import SubscribePacket
from asyncmqtt.packet_suback import SubackPacket
from asyncmqtt.packet_publish import PublishPacket


PACKET_TYPES = {
    CONNECT: ConnectPacket,
    CONNACK: ConnackPacket,
    PUBLISH: PublishPacket,
    SUBSCRIBE: SubscribePacket,
    SUBACK: SubackPacket,
    PINGREQ: PingReqPacket,
    PINGRESP: PingRespPacket,
}


class MQTTClientProtocol(asyncio.Protocol):
    def __init__(self):
        self.msgq = asyncio.Queue()
        self.buffer = bytearray()
        self.transport = None
        self.packet_id = 0

    @property
    def next_packet_id(self):
        self.packet_id += 1
        return self.packet_id % 65535

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.buffer.extend(data)
        self.decode_buffer()

    def decode_buffer(self):
        global PACKET_TYPES

        while self.buffer:
            try:
                fixed = MQTTFixedHeader.from_bytes(self.buffer)
            except MQTTException:
                return

            msgsize = fixed.bytes_length + fixed.remaining_length
            workbuf = self.buffer[:msgsize]
            self.buffer = self.buffer[msgsize:]

            ptcons = PACKET_TYPES.get(fixed.packet_type, None)
            if not ptcons:
                print('Undefined handler for packet type %x' % fixed.packet_type)

            packet = ptcons.from_bytes(workbuf)
            self.msgq.put_nowait(packet)

    def connect(self, username: str=None, password: str=None):
        cp = ConnectPacket()
        if username:
            cp.username = username
        if password:
            cp.password = password
        self.transport.write(cp.to_bytes())

    def subscribe(self, topics):
        sp = SubscribePacket.build(topics, self.next_packet_id)
        self.transport.write(sp.to_bytes())

    async def next_message(self):
        msg = await self.msgq.get()
        return msg
