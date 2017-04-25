from asyncmqtt import MQTTException
from asyncmqtt.packet import MQTTFixedHeader, MQTTVariableHeader, MQTTPayload, MQTTPacket, SUBACK, PacketIDVariableHeader
from asyncmqtt.util import *


class SubackPayload(MQTTPayload):
    RETURN_CODE_00 = 0x00
    RETURN_CODE_01 = 0x01
    RETURN_CODE_02 = 0x02
    RETURN_CODE_80 = 0x80

    def __init__(self, return_codes=[]):
        self.return_codes = return_codes

    def __repr__(self):
        return type(self).__name__ + '(return_codes={0})'.format(repr(self.return_codes))

    def to_bytes(self, fixed_header: MQTTFixedHeader, variable_header: MQTTVariableHeader):
        out = b''
        for return_code in self.return_codes:
            out += int_to_bytes(return_code, 1)
        return out

    @classmethod
    def from_bytes(cls, buffer: bytearray, fixed_header: MQTTFixedHeader,
                   variable_header: MQTTVariableHeader):
        return_codes = []
        length = fixed_header.remaining_length - variable_header.bytes_length
        for i in range(0, length):
            return_codes.append(buffer[i])
        return cls(return_codes)


class SubackPacket(MQTTPacket):
    VARIABLE_HEADER = PacketIDVariableHeader
    PAYLOAD = SubackPayload

    def __init__(self, fixed: MQTTFixedHeader=None, variable_header: PacketIDVariableHeader=None, payload=None):
        if fixed is None:
            header = MQTTFixedHeader(SUBACK, 0x00)
        else:
            if fixed.packet_type is not SUBACK:
                raise MQTTException("Invalid fixed packet type %s for SubackPacket init" % fixed.packet_type)
            header = fixed

        super().__init__(header)
        self.variable_header = variable_header
        self.payload = payload

    @property
    def return_codes(self):
        return self.payload.return_codes

    @return_codes.setter
    def return_codes_set(self, return_codes):
        self.payload.return_codes = return_codes

    @classmethod
    def build(cls, packet_id, return_codes):
        variable_header = cls.VARIABLE_HEADER(packet_id)
        payload = cls.PAYLOAD(return_codes)
        return cls(variable_header=variable_header, payload=payload)
