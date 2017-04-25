asyncmqtt -- a fast MQTT client library for Python/asyncio
==========================================================

**asyncmqtt** is a client library designed specifically to run as an asyncio Protocol.
asyncmqtt is a clean, efficient design which borrows the MQTT protocol parsers from
`HBMQTT <http://github.com/beerfactory/hbmqtt>`_ and combines them with a new implementation
built around ``asyncio.Protocol``.

asyncmqtt requires Python 3.5 or later and presently supports basic MQTT features (QoS 0/1, but
not yet QoS 2).  It is intended to be a "low level" type interface: your application should fully
handle the logistics of actually processing the messages, unlike HBMQTT.


Performance
-----------

In my testing asyncmqtt is roughly 4 to 5 times faster than HBMQTT for the most common usecase
(processing ``PUBLISH`` message streams).
