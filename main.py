from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog
import sys
from opcua_client import OPCUAClient
from gui import MainWindow
from login_dialog import LoginDialog
from select_client import SelectClientDialog
from node_options import CLINIC_OPTIONS, CLIENT_OPTIONS, CLIENT_LIST

NODES = [
    ("ClientName", "ns=2;i=211"),
    ("MaterialType", "ns=2;i=217"),
    ("Color", "ns=2;i=226"),
    ("Frame brand", "ns=2;i=229"),
    ("LensType", "ns=2;i=235"),
    ("VisionCondition", "ns=2;i=241"),
    ("UsageState", "ns=2;i=168"),
    ("LensCondition", "ns=2;i=174"),
    ("FrameIntegrity", "ns=2;i=180"),
    ("LastRevisionDate", "ns=2;i=183"),
]

def main_application_loop():
    app = QApplication(sys.argv)
    
    while True:
        # Login dialog
        login = LoginDialog()
        if login.exec_() != QDialog.Accepted:
            break  # User cancelled login

        username, password = login.get_credentials()
        opcua_client = OPCUAClient(username=username, password=password)

        try:
            opcua_client.connect()
        except Exception as e:
            QMessageBox.critical(None, "Login Failed", f"Could not connect: {e}")
            continue  # Try login again

        # Only admin can select client
        if username == "admin":
            select_client = SelectClientDialog(CLIENT_LIST)
            if select_client.exec_() != QDialog.Accepted:
                opcua_client.disconnect()
                continue
            selected_client = select_client.get_selected_client()
        else:
            selected_client = username  # Regular users only see their own data

        user_type = "clinic" if username == "admin" else "client"
        window = MainWindow(NODES, user_type=user_type, opcua_client=opcua_client, username=selected_client)
        window.set_client_name(selected_client)

        # Connect logout
        window.logout_requested.connect(app.quit)

        window.show()
        # Add this block to refresh values
        def refresh_all():
            for label, node_id in NODES:
                try:
                    value = opcua_client.read_node(node_id)
                    window.set_node_value(node_id, value)
                except Exception as e:
                    window.set_node_value(node_id, f"Error: {e}")

        refresh_all()
        app.exec_()
        opcua_client.disconnect()

if __name__ == "__main__":
    main_application_loop()