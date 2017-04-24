from asyncmqtt.packet import MQTTException, MQTTPacket, MQTTFixedHeader, PINGREQ, PINGRESP


class PingReqPacket(MQTTPacket):
    VARIABLE_HEADER = None
    PAYLOAD = None

    def __init__(self, fixed: MQTTFixedHeader=None):
        if not fixed:
            fixed = MQTTFixedHeader(PINGREQ)
        assert fixed.packet_type == PINGREQ
        super().__init__(fixed)


class PingRespPacket(MQTTPacket):
    VARIABLE_HEADER = None
    PAYLOAD = None

    def __init__(self, fixed: MQTTFixedHeader=None):
        if not fixed:
            fixed = MQTTFixedHeader(PINGRESP)
        assert fixed.packet_type == PINGRESP
        super().__init__(fixed)
