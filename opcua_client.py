from opcua import Client

class OPCUAClient:
    def __init__(self, url="opc.tcp://localhost:4840"):
        self.url = url
        self.client = Client(self.url)

    def connect(self):
        self.client.connect()

    def disconnect(self):
        self.client.disconnect()

    def read_node(self, node_id):
        node = self.client.get_node(node_id)
        return node.get_value()

    def write_node(self, node_id, value):
        node = self.client.get_node(node_id)
        node.set_value(value) 