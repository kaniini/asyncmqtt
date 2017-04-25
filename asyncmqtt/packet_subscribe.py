from asyncmqtt import MQTTException
from asyncmqtt.packet import MQTTFixedHeader, MQTTVariableHeader, MQTTPayload, MQTTPacket, SUBSCRIBE, PacketIDVariableHeader
from asyncmqtt.util import *


class SubscribePayload(MQTTPayload):
    def __init__(self, topics=[]):
        super().__init__()
        self.topics = topics

    def to_bytes(self, fixed_header: MQTTFixedHeader, variable_header: MQTTVariableHeader):
        out = b''
        for topic in self.topics:
            out += encode_string(topic[0])
            out += int_to_bytes(topic[1], 1)
        return out

    @classmethod
    def from_bytes(cls, buffer: bytearray, fixed_header: MQTTFixedHeader,
                   variable_header: MQTTVariableHeader):
        topics = []
        payload_length = fixed_header.remaining_length - variable_header.bytes_length
        needle = 0
        while needle < payload_length:
            topic = decode_string(buffer[needle:])
            needle += 2 + len(topic.encode('utf-8'))
            qos = buffer[needle]
            needle += 1
            topics.append((topic, qos))
        return cls(topics)

    def __repr__(self):
        return type(self).__name__ + '(topics={0!r})'.format(self.topics)


class SubscribePacket(MQTTPacket):
    VARIABLE_HEADER = PacketIDVariableHeader
    PAYLOAD = SubscribePayload

    def __init__(self, fixed: MQTTFixedHeader=None, variable_header: PacketIDVariableHeader=None, payload=None):
        if fixed is None:
            header = MQTTFixedHeader(SUBSCRIBE, 0x02) # [MQTT-3.8.1-1]
        else:
            if fixed.packet_type is not SUBSCRIBE:
                raise MQTTException("Invalid fixed packet type %s for SubscribePacket init" % fixed.packet_type)
            header = fixed

        super().__init__(header)
        self.variable_header = variable_header
        self.payload = payload

    @property
    def topics(self):
        return self.payload.topics

    @topics.setter
    def topics_set(self, topics):
        self.payload.topics = topics

    @classmethod
    def build(cls, topics, packet_id):
        v_header = PacketIDVariableHeader(packet_id)
        payload = SubscribePayload(topics)
        return SubscribePacket(variable_header=v_header, payload=payload)
