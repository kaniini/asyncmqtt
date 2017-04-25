from asyncmqtt import MQTTException
from asyncmqtt.packet import MQTTFixedHeader, MQTTVariableHeader, MQTTPayload, MQTTPacket, CONNACK
from asyncmqtt.util import *


CONNECTION_ACCEPTED = 0x00
UNACCEPTABLE_PROTOCOL_VERSION = 0x01
IDENTIFIER_REJECTED = 0x02
SERVER_UNAVAILABLE = 0x03
BAD_USERNAME_PASSWORD = 0x04
NOT_AUTHORIZED = 0x05


class ConnackVariableHeader(MQTTVariableHeader):
    def __init__(self, return_code=None):
        super().__init__()
        self.return_code = return_code

    @classmethod
    def from_bytes(cls, buffer: bytearray, fixed_header: MQTTFixedHeader):
        data = buffer[0:2]
        return_code = data[1]
        return cls(return_code)

    def to_bytes(self):
        out = bytearray(2)

        out[0] = 0
        out[1] = self.return_code

        return out

    def __repr__(self):
        return type(self).__name__ + ('(return_code=%x)' % self.return_code)


class ConnackPacket(MQTTPacket):
    VARIABLE_HEADER = ConnackVariableHeader
    PAYLOAD = None

    @property
    def return_code(self):
        return self.variable_header.return_code

    @return_code.setter
    def return_code(self, return_code):
        self.variable_header.return_code = return_code

    def __init__(self, fixed: MQTTFixedHeader=None, variable_header: ConnackVariableHeader=None, payload=None):
        if fixed is None:
            header = MQTTFixedHeader(CONNACK, 0x00)
        else:
            if fixed.packet_type is not CONNACK:
                raise MQTTException("Invalid fixed packet type %s for ConnackPacket init" % fixed.packet_type)
            header = fixed
        super().__init__(header)
        self.variable_header = variable_header
        self.payload = None

    @classmethod
    def build(cls, return_code=None):
        v_header = ConnackVariableHeader(return_code)
        packet = ConnackPacket(variable_header=v_header)
        return packet
