from PyQt5.QtWidgets import QApplication
import sys
from opcua_client import OPCUAClient
from gui import MainWindow

NODES = [
    ("Client name", "ns=2;i=211"),
    ("Frame material", "ns=2;i=217"),
    ("Frame color", "ns=2;i=226"),
    ("Frame brand", "ns=2;i=229"),
    ("Lens type", "ns=2;i=235"),
    ("Vision condition", "ns=2;i=241"),
    ("Usage state", "ns=2;i=168"),
    ("Lens condition", "ns=2;i=174"),
    ("Frame integrity", "ns=2;i=180"),
    ("Last revision date", "ns=2;i=183"),
]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    opcua_client = OPCUAClient()
    opcua_client.connect()

    # Change betwwen "clinic" o "client"
    window = MainWindow(NODES, user_type="clinic")

    def refresh_all():
        for label, node_id in NODES:
            try:
                value = opcua_client.read_node(node_id)
                window.set_node_value(node_id, value)
            except Exception as e:
                window.set_node_value(node_id, f"Error: {e}")

    for node_widget in window.get_node_widgets():
        def make_write_func(node_id, input_field):
            def write_func():
                if hasattr(input_field, "date") and hasattr(input_field, "setCalendarPopup"):
                    value = input_field.date().toString("yyyy-MM-dd")
                else:
                    value = input_field.currentText()
                try:
                    opcua_client.write_node(node_id, value)
                    refresh_all()
                except Exception as e:
                    window.set_node_value(node_id, f"Error: {e}")
            return write_func
        node_widget.write_button.clicked.connect(make_write_func(node_widget.node_id, node_widget.input))

    window.refresh_button.clicked.connect(refresh_all)
    window.show()
    refresh_all()
    app.exec_()
    opcua_client.disconnect()