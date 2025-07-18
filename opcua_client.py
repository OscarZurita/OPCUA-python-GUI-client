from asyncua import Client, ua
import asyncio

class OPCUAClient:
    def __init__(self, url="opc.tcp://localhost:4840", username=None, password=None):
        self.url = url
        self.username = username
        self.password = password
        self.client = None

    def ensure_connected(self):
        # Try to check if the client and session are active, reconnect if not
        try:
            if not self.client or not getattr(self.client, 'session', None) or not self.client.session.active:
                self.connect()
        except Exception:
            self.connect()

    def connect(self):
        # Create event loop if it doesn't exist
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the async connect
        loop.run_until_complete(self._async_connect())

    async def _async_connect(self):
        self.client = Client(self.url)
        if self.username and self.password:
            self.client.set_user(self.username)
            self.client.set_password(self.password)
        await self.client.connect()

    def disconnect(self):
        try:
            if self.client:
                # Create event loop if it doesn't exist
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Run the async disconnect
                loop.run_until_complete(self._async_disconnect())
        except Exception as e:
            # Ignore disconnect errors - socket might already be closed
            print(f"Disconnect warning: {e}")
            pass

    async def _async_disconnect(self):
        if self.client:
            await self.client.disconnect()

    def read_node(self, node_id):
        if not self.client:
            raise Exception("Client not connected")
        
        # Create event loop if it doesn't exist
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the async read
        return loop.run_until_complete(self._async_read_node(node_id))

    async def _async_read_node(self, node_id):
        node = self.client.get_node(node_id)
        return await node.read_value()

    def write_node(self, node_id, value):
        if not self.client:
            raise Exception("Client not connected")
        
        # Create event loop if it doesn't exist
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the async write
        loop.run_until_complete(self._async_write_node(node_id, value))

    async def _async_write_node(self, node_id, value):
        node = self.client.get_node(node_id)
        variant_type = await node.read_data_type_as_variant_type()
        dv = ua.DataValue(ua.Variant(value, variant_type))
        await node.write_value(dv)