from asyncmqtt import MQTTException
from asyncmqtt.packet import MQTTFixedHeader, MQTTVariableHeader, MQTTPayload, MQTTPacket, CONNECT
from asyncmqtt.util import *


class ConnectVariableHeader(MQTTVariableHeader):
    USERNAME_FLAG = 0x80
    PASSWORD_FLAG = 0x40
    WILL_RETAIN_FLAG = 0x20
    WILL_FLAG = 0x04
    WILL_QOS_MASK = 0x18
    CLEAN_SESSION_FLAG = 0x02
    RESERVED_FLAG = 0x01

    def __init__(self, connect_flags=0, keep_alive=0, proto_name='MQTT', proto_level=0x04):
        self.proto_name = proto_name
        self.proto_level = proto_level
        self.flags = connect_flags
        self.keep_alive = keep_alive

    def __repr__(self):
        return "ConnectVariableHeader(proto_name={0}, proto_level={1}, flags={2}, keepalive={3})".format(
            self.proto_name, self.proto_level, hex(self.flags), self.keep_alive)

    def _set_flag(self, val, mask):
        if val:
            self.flags |= mask
        else:
            self.flags &= ~mask

    def _get_flag(self, mask):
        if self.flags & mask:
            return True
        else:
            return False

    @property
    def username_flag(self) -> bool:
        return self._get_flag(self.USERNAME_FLAG)

    @username_flag.setter
    def username_flag(self, val: bool):
        self._set_flag(val, self.USERNAME_FLAG)

    @property
    def password_flag(self) -> bool:
        return self._get_flag(self.PASSWORD_FLAG)

    @password_flag.setter
    def password_flag(self, val: bool):
        self._set_flag(val, self.PASSWORD_FLAG)

    @property
    def will_retain_flag(self) -> bool:
        return self._get_flag(self.WILL_RETAIN_FLAG)

    @will_retain_flag.setter
    def will_retain_flag(self, val: bool):
        self._set_flag(val, self.WILL_RETAIN_FLAG)

    @property
    def will_flag(self) -> bool:
        return self._get_flag(self.WILL_FLAG)

    @will_flag.setter
    def will_flag(self, val: bool):
        self._set_flag(val, self.WILL_FLAG)

    @property
    def clean_session_flag(self) -> bool:
        return self._get_flag(self.CLEAN_SESSION_FLAG)

    @clean_session_flag.setter
    def clean_session_flag(self, val: bool):
        self._set_flag(val, self.CLEAN_SESSION_FLAG)

    @property
    def reserved_flag(self) -> bool:
        return self._get_flag(self.RESERVED_FLAG)

    @property
    def will_qos(self):
        return (self.flags & 0x18) >> 3

    @will_qos.setter
    def will_qos(self, val: int):
        self.flags &= 0xe7  # Reset QOS flags
        self.flags |= (val << 3)

    @classmethod
    def from_bytes(cls, buffer: bytes, fixed_header: MQTTFixedHeader):
        needle = 0

        protocol_name = decode_string(buffer[needle:])
        needle += 2 + len(protocol_name)

        # protocol level
        protocol_level = buffer[needle]
        needle += 1

        # flags
        flags = buffer[needle]
        needle += 1

        # keep-alive
        keep_alive = bytes_to_int(buffer[needle:][:2])

        return cls(flags, keep_alive, protocol_name, protocol_level)

    def to_bytes(self):
        out = bytearray()

        # Protocol name
        out.extend(encode_string(self.proto_name))
        # Protocol level
        out.append(self.proto_level)
        # flags
        out.append(self.flags)
        # keep alive
        out.extend(int_to_bytes(self.keep_alive, 2))

        return out


class ConnectPayload(MQTTPayload):
    def __init__(self, client_id=None, will_topic=None, will_message=None, username=None, password=None):
        super().__init__()
        self.client_id = client_id
        self.will_topic = will_topic
        self.will_message = will_message
        self.username = username
        self.password = password
        if not self.client_id:
            self.client_id = gen_client_id()

    def __repr__(self):
        return "ConnectPayload(client_id={0}, will_topic={1}, will_message={2}, username={3}, password={4})".\
            format(self.client_id, self.will_topic, self.will_message, self.username, self.password)

    @classmethod
    def from_bytes(cls, buffer: bytes, fixed_header: MQTTFixedHeader,
                    variable_header: ConnectVariableHeader):
        needle = 0
        payload = cls()
        payload.client_id = decode_string(buffer)

        needle += 2 + len(payload.client_id)

        # Read will topic, username and password
        if variable_header.will_flag:
            payload.will_topic = decode_string(buffer[needle:])
            needle += 2 + len(payload.will_topic)
            payload.will_message = decode_data(buffer[needle:])
            needle += 2 + len(payload.will_message)

        if variable_header.username_flag:
            payload.username = decode_string(buffer[needle:])
            needle += 2 + len(payload.username)

        if variable_header.password_flag:
            payload.password = decode_string(buffer[needle:])

        return payload

    def to_bytes(self, fixed_header: MQTTFixedHeader, variable_header: ConnectVariableHeader):
        out = bytearray()

        # Client identifier
        out.extend(encode_string(self.client_id))

        # Will topic / message
        if variable_header.will_flag:
            out.extend(encode_string(self.will_topic))
            out.extend(encode_data_with_length(self.will_message))

        # username
        if variable_header.username_flag:
            out.extend(encode_string(self.username))

        # password
        if variable_header.password_flag:
            out.extend(encode_string(self.password))

        return out


class ConnectPacket(MQTTPacket):
    VARIABLE_HEADER = ConnectVariableHeader
    PAYLOAD = ConnectPayload

    @property
    def proto_name(self):
        return self.variable_header.proto_name

    @proto_name.setter
    def proto_name(self, name: str):
        self.variable_header.proto_name = name

    @property
    def proto_level(self):
        return self.variable_header.proto_level

    @proto_level.setter
    def proto_level(self, level):
        self.variable_header.proto_level = level

    @property
    def username_flag(self):
        return self.variable_header.username_flag

    @username_flag.setter
    def username_flag(self, flag):
        self.variable_header.username_flag = flag

    @property
    def password_flag(self):
        return self.variable_header.password_flag

    @password_flag.setter
    def password_flag(self, flag):
        self.variable_header.password_flag = flag

    @property
    def clean_session_flag(self):
        return self.variable_header.clean_session_flag

    @clean_session_flag.setter
    def clean_session_flag(self, flag):
        self.variable_header.clean_session_flag = flag

    @property
    def will_retain_flag(self):
        return self.variable_header.will_retain_flag

    @will_retain_flag.setter
    def will_retain_flag(self, flag):
        self.variable_header.will_retain_flag = flag

    @property
    def will_qos(self):
        return self.variable_header.will_qos

    @will_qos.setter
    def will_qos(self, flag):
        self.variable_header.will_qos = flag

    @property
    def will_flag(self):
        return self.variable_header.will_flag

    @will_flag.setter
    def will_flag(self, flag):
        self.variable_header.will_flag = flag

    @property
    def reserved_flag(self):
        return self.variable_header.reserved_flag

    @reserved_flag.setter
    def reserved_flag(self, flag):
        self.variable_header.reserved_flag = flag

    @property
    def client_id(self):
        return self.payload.client_id

    @client_id.setter
    def client_id(self, client_id):
        self.payload.client_id = client_id

    @property
    def will_topic(self):
        return self.payload.will_topic

    @will_topic.setter
    def will_topic(self, will_topic):
        self.payload.will_topic = will_topic

    @property
    def will_message(self):
        return self.payload.will_message

    @will_message.setter
    def will_message(self, will_message):
        self.payload.will_message = will_message

    @property
    def username(self):
        return self.payload.username

    @username.setter
    def username(self, username):
        self.variable_header.username_flag = username is not None
        self.payload.username = username

    @property
    def password(self):
        return self.payload.password

    @password.setter
    def password(self, password):
        self.variable_header.password_flag = password is not None
        self.payload.password = password

    @property
    def keep_alive(self):
        return self.variable_header.keep_alive

    @keep_alive.setter
    def keep_alive(self, keep_alive):
        self.variable_header.keep_alive = keep_alive

    def __init__(self, fixed: MQTTFixedHeader=None, vh: ConnectVariableHeader=None, payload: ConnectPayload=None):
        if fixed is None:
            header = MQTTFixedHeader(CONNECT, 0x00)
        else:
            if fixed.packet_type is not CONNECT:
                raise MQTTException("Invalid fixed packet type %s for ConnectPacket init" % fixed.packet_type)
            header = fixed
        super().__init__(header)
        if not vh:
            vh = ConnectVariableHeader()
        if not payload:
            payload = ConnectPayload()
        self.variable_header = vh
        self.payload = payload
