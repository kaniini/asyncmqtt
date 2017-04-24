import struct
import asyncio


RESERVED_0 = 0x00
CONNECT = 0x01
CONNACK = 0x02
PUBLISH = 0x03
PUBACK = 0x04
PUBREC = 0x05
PUBREL = 0x06
PUBCOMP = 0x07
SUBSCRIBE = 0x08
SUBACK = 0x09
UNSUBSCRIBE = 0x0a
UNSUBACK = 0x0b
PINGREQ = 0x0c
PINGRESP = 0x0d
DISCONNECT = 0x0e
RESERVED_15 = 0x0f


class MQTTException(ValueError):
    pass


class MQTTFixedHeader:
    def __init__(self, packet_type, flags=0, length=0):
        self.packet_type = packet_type
        self.remaining_length = length
        self.flags = flags

    def to_bytes(self):
        def encode_remaining_length(length: int):
            encoded = bytearray()
            while True:
                length_byte = length % 0x80
                length //= 0x80
                if length > 0:
                    length_byte |= 0x80
                encoded.append(length_byte)
                if length <= 0:
                    break
            return encoded

        out = bytearray()
        packet_type = 0
        try:
            packet_type = (self.packet_type << 4) | self.flags
            out.append(packet_type)
        except OverflowError:
            raise MQTTException('packet_type encoding exceed 1 byte length: value=%d', packet_type)

        encoded_length = encode_remaining_length(self.remaining_length)
        out.extend(encoded_length)

        return out

    @property
    def bytes_length(self):
        return len(self.to_bytes())

    @classmethod
    def from_bytes(cls, buffer: bytearray):
        """
        Read and decode MQTT message fixed header from stream
        :return: FixedHeader instance
        """
        def decode_remaining_length(buffer: bytearray):
            """
            Decode message length according to MQTT specifications
            :return:
            """
            multiplier = 1
            value = 0
            valid = False
            for enc_byte in buffer:
                value += (enc_byte & 0x7f) * multiplier
                if (enc_byte & 0x80) == 0:
                    valid = True
                    break
                else:
                    multiplier *= 128
                    if multiplier > 128 * 128 * 128:
                        raise MQTTException("Invalid remaining length bytes:%r, packet_type=%d" % (buffer, msg_type))

            if not valid:
                raise MQTTException("Packet is truncated")

            return value

        int1 = struct.unpack('!B', buffer[0:1])
        msg_type = (int1[0] & 0xf0) >> 4
        flags = int1[0] & 0x0f
        remain_length = decode_remaining_length(buffer[1:])

        return cls(msg_type, flags, remain_length)

    def __repr__(self):
        return type(self).__name__ + '(length={0}, flags={1})'.\
            format(self.remaining_length, hex(self.flags))


class MQTTVariableHeader:
    def to_bytes(self):
        """Marshal header data to bytes."""
        raise NotImplementedError()

    @property
    def bytes_length(self):
        return len(self.to_bytes())

    @classmethod
    def from_bytes(cls, buffer: bytearray):
        """Demarshal header data from bytes."""
        raise NotImplementedError()


class MQTTPayload:
    def to_bytes(self):
        """Marshal payload data to bytes."""
        raise NotImplementedError()

    @classmethod
    def from_bytes(cls, buffer: bytearray, fixed_header: MQTTFixedHeader, variable_header: MQTTVariableHeader):
        """Demarshal payload data from bytes.  In most cases, the default implementation is adequate."""
        needle = fixed_header.bytes_length + variable_header.bytes_length
        if needle > len(buffer):
            raise MQTTException('packet truncated')
        return cls(buffer[needle:])
