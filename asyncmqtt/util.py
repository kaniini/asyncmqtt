import random

from asyncmqtt import MQTTException


def bytes_as_hex(data: bytes) -> str:
    return ' '.join(format(b, '02x') for b in data)


def bytes_to_int(data: bytes) -> int:
    return int.from_bytes(data, byteorder='big')


def int_to_bytes(data: int, length: int) -> bytes:
    return data.to_bytes(length, byteorder='big')


def encode_string(string: str) -> bytes:
    payload = string.encode('utf-8')
    return int_to_bytes(len(payload), 2) + payload


def decode_string(data: bytes) -> str:
    if len(data) < 2:
        raise MQTTException('packet not large enough to contain any data, length=%d' % len(data))

    data_len = bytes_to_int(data[0:2])
    if not data_len:
        return ''

    return data[2:2 + data_len].decode('utf-8')


def gen_client_id() -> str:
    return 'asyncmqtt/' + ''.join(format(random.randint(0, 256), '02x') for i in range(10))
