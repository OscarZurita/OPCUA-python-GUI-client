from PyQt5.QtWidgets import QApplication
import sys
from opcua_client import OPCUAClient
from gui import MainWindow

NODE_ID = "ns=2;i=2"  # Change this to a valid node on your server

if __name__ == "__main__":
    app = QApplication(sys.argv)
    opcua_client = OPCUAClient()
    opcua_client.connect()

    window = MainWindow()

    def refresh_value():
        try:
            value = opcua_client.read_node(NODE_ID)
            window.set_value(value)
        except Exception as e:
            window.set_value(f"Error: {e}")

    window.refresh_button.clicked.connect(refresh_value)
    window.show()
    refresh_value()  # Initial value
    app.exec_()
    opcua_client.disconnect() 