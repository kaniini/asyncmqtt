from asyncmqtt import MQTTException
from asyncmqtt.packet import MQTTFixedHeader, MQTTVariableHeader, MQTTPayload, MQTTPacket, PUBLISH, PacketIDVariableHeader
from asyncmqtt.util import *


class PublishVariableHeader(MQTTVariableHeader):
    def __init__(self, topic_name: str, packet_id: int=None):
        super().__init__()
        if '*' in topic_name:
            raise MQTTException("[MQTT-3.3.2-2] Topic name in the PUBLISH Packet MUST NOT contain wildcard characters.")
        self.topic_name = topic_name
        self.packet_id = packet_id

    def __repr__(self):
        return type(self).__name__ + '(topic={0}, packet_id={1})'.format(self.topic_name, self.packet_id)

    def to_bytes(self):
        out = bytearray()
        out.extend(encode_string(self.topic_name))
        if self.packet_id is not None:
            out.extend(int_to_bytes(self.packet_id, 2))
        return out

    @classmethod
    def from_bytes(cls, buffer: bytearray, fixed_header: MQTTFixedHeader):
        topic_name = decode_string(buffer)
        needle = 2 + len(topic_name)
        has_qos = (fixed_header.flags >> 1) & 0x03
        if has_qos:
            packet_id = bytes_to_int(buffer[needle:needle + 2])
        else:
            packet_id = None
        return cls(topic_name, packet_id)


class PublishPayload(MQTTPayload):
    def __init__(self, data: bytes=None):
        super().__init__()
        self.data = data

    def __repr__(self):
        return type(self).__name__ + '(data={0!r})'.format(repr(self.data))

    def to_bytes(self, fixed_header: MQTTFixedHeader, variable_header: MQTTVariableHeader):
        return self.data


class PublishPacket(MQTTPacket):
    VARIABLE_HEADER = PublishVariableHeader
    PAYLOAD = PublishPayload

    DUP_FLAG = 0x08
    RETAIN_FLAG = 0x01
    QOS_FLAG = 0x06

    def __init__(self, fixed: MQTTFixedHeader=None, variable_header: PublishVariableHeader=None, payload=None):
        if fixed is None:
            header = MQTTFixedHeader(PUBLISH, 0x00)
        else:
            if fixed.packet_type is not PUBLISH:
                raise HBMQTTException("Invalid fixed packet type %s for PublishPacket init" % fixed.packet_type)
            header = fixed

        super().__init__(header)
        self.variable_header = variable_header
        self.payload = payload

    def set_flags(self, dup_flag=False, qos=0, retain_flag=False):
        self.dup_flag = dup_flag
        self.retain_flag = retain_flag
        self.qos = qos

    def _set_header_flag(self, val, mask):
        if val:
            self.fixed_header.flags |= mask
        else:
            self.fixed_header.flags &= ~mask

    def _get_header_flag(self, mask):
        if self.fixed_header.flags & mask:
            return True
        else:
            return False

    @property
    def dup_flag(self) -> bool:
        return self._get_header_flag(self.DUP_FLAG)

    @dup_flag.setter
    def dup_flag(self, val: bool):
        self._set_header_flag(val, self.DUP_FLAG)

    @property
    def retain_flag(self) -> bool:
        return self._get_header_flag(self.RETAIN_FLAG)

    @retain_flag.setter
    def retain_flag(self, val: bool):
        self._set_header_flag(val, self.RETAIN_FLAG)

    @property
    def qos(self):
        return (self.fixed_header.flags & self.QOS_FLAG) >> 1

    @qos.setter
    def qos(self, val: int):
        self.fixed_header.flags &= 0xf9
        self.fixed_header.flags |= (val << 1)

    @property
    def packet_id(self):
        return self.variable_header.packet_id

    @packet_id.setter
    def packet_id(self, val: int):
        self.variable_header.packet_id = val

    @property
    def data(self):
        return self.payload.data

    @data.setter
    def data(self, data: bytes):
        self.payload.data = data

    @property
    def topic_name(self):
        return self.variable_header.topic_name

    @topic_name.setter
    def topic_name(self, name: str):
        self.variable_header.topic_name = name

    @classmethod
    def build(cls, topic_name: str, message: bytes, packet_id: int, dup_flag, qos, retain):
        v_header = PublishVariableHeader(topic_name, packet_id)
        payload = PublishPayload(message)
        packet = PublishPacket(variable_header=v_header, payload=payload)
        packet.dup_flag = dup_flag
        packet.retain_flag = retain
        packet.qos = qos
        return packet
