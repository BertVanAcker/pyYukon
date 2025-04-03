import uasyncio as asyncio
import usocket as socket
import struct

class NonBlockingMQTTClient:
    def __init__(self, client_id, server, port=1883, keepalive=60):
        self.client_id = client_id
        self.server = server
        self.port = port
        self.keepalive = keepalive
        self.reader = None
        self.writer = None
        self.subscriptions = {}  # topic -> callback coroutine
        self.connected = False
        #self.message_queue = asyncio.Queue()  # For messages without a registered callback

    async def connect(self):
        # Open a connection to the MQTT broker
        self.reader, self.writer = await asyncio.open_connection(self.server, self.port)
        # Build and send the CONNECT packet
        packet = self._build_connect_packet()
        self.writer.write(packet)
        await self.writer.drain()
        # Wait for CONNACK (we assume a 4-byte response)
        connack = await self.reader.read(4)
        if connack[3] != 0:  # The fourth byte is the Connect Return Code (0 = success)
            raise Exception("MQTT connection failed with error code {}".format(connack[3]))
        self.connected = True
        # Start the background task that reads incoming packets
        asyncio.create_task(self._read_loop())

    def _build_connect_packet(self):
        # MQTT CONNECT packet consists of a fixed header, variable header, and payload
        # Variable header: Protocol Name ("MQTT"), Protocol Level (4), Connect Flags, Keep Alive
        proto = b'\x00\x04MQTT'
        ver = b'\x04'
        flags = b'\x02'  # Clean session flag set
        keepalive = struct.pack("!H", self.keepalive)
        client_id_encoded = self._encode_string(self.client_id)
        variable_header = proto + ver + flags + keepalive
        payload = client_id_encoded
        remaining = self._encode_length(len(variable_header) + len(payload))
        packet = b'\x10' + remaining + variable_header + payload
        return packet

    def _encode_string(self, s):
        encoded = s.encode('utf-8')
        return struct.pack("!H", len(encoded)) + encoded

    def _encode_length(self, length):
        # MQTT uses a variable-length encoding for the remaining length.
        encoded = b""
        while True:
            digit = length % 128
            length //= 128
            if length > 0:
                digit |= 0x80
            encoded += bytes([digit])
            if length == 0:
                break
        return encoded

    async def _read_loop(self):
        try:
            while self.connected:
                # Read the fixed header (at least one byte)
                header = await self.reader.read(1)
                if not header:
                    break
                packet_type = header[0] >> 4

                # Read the remaining length using MQTT's variable-length encoding
                remaining_length = 0
                multiplier = 1
                while True:
                    b = await self.reader.read(1)
                    if not b:
                        break
                    digit = b[0]
                    remaining_length += (digit & 127) * multiplier
                    multiplier *= 128
                    if not (digit & 128):
                        break

                payload = await self.reader.read(remaining_length)
                # Handle packets based on their type
                if packet_type == 3:  # PUBLISH packet
                    await self._handle_publish(payload)
                # (Add support for other packet types as needed)
        except Exception as e:
            print("Read loop error:", e)
            self.connected = False

    async def _handle_publish(self, payload):
        # MQTT PUBLISH packet: topic string followed by message payload.
        topic_length = struct.unpack("!H", payload[0:2])[0]
        topic = payload[2:2+topic_length].decode('utf-8')
        message = payload[2+topic_length:]
        # If a subscription callback is registered for this topic, call it
        if topic in self.subscriptions:
            await self.subscriptions[topic](topic, message)
        #else:
        #    # Otherwise, queue the message for later processing
        #    await self.message_queue.put((topic, message))

    async def publish(self, topic, message, qos=0):
        # Build a simple PUBLISH packet (only supporting QoS 0)
        topic_encoded = self._encode_string(topic)
        if isinstance(message, str):
            message_bytes = message.encode('utf-8')
        else:
            message_bytes = message
        fixed_header = b'\x30'  # PUBLISH with QoS 0, no retain flag
        remaining = self._encode_length(len(topic_encoded) + len(message_bytes))
        packet = fixed_header + remaining + topic_encoded + message_bytes
        self.writer.write(packet)
        await self.writer.drain()

    async def subscribe(self, topic, callback, qos=0):
        # Build a SUBSCRIBE packet.
        # Note: For simplicity, this example uses a fixed packet identifier (should be unique in production).
        packet_id = 1
        topic_encoded = self._encode_string(topic)
        packet_payload = topic_encoded + bytes([qos])
        variable_header = struct.pack("!H", packet_id)
        remaining = self._encode_length(len(variable_header) + len(packet_payload))
        packet = b'\x82' + remaining + variable_header + packet_payload
        self.writer.write(packet)
        await self.writer.drain()
        # Save the callback coroutine to be called when a message is received on this topic.
        self.subscriptions[topic] = callback

    async def disconnect(self):
        # Build and send a DISCONNECT packet.
        packet = b'\xe0\x00'
        self.writer.write(packet)
        await self.writer.drain()
        self.writer.close()
        await self.writer.wait_closed()
        self.connected = False
