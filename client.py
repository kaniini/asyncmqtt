import asyncio
import sys
import uvloop


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()


from asyncmqtt.client import MQTTClientProtocol
from asyncmqtt.packet_publish import PublishPacket


async def main():
     print('starting')
     conn, client = await loop.create_connection(MQTTClientProtocol, sys.argv[1], int(sys.argv[2]))
     client.connect(sys.argv[3], sys.argv[4])
     client.subscribe([(sys.argv[5] + '/#', 0)])

     while True:
         message = await client.next_message()
         if type(message) == PublishPacket:
             print(message.variable_header.topic_name, '=>', message.payload.data.decode('utf-8'))


asyncio.ensure_future(main())
loop.run_forever()
