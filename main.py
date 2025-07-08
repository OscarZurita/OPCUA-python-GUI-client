from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog
import sys
from opcua_client import OPCUAClient
from gui import MainWindow
from login_dialog import LoginDialog

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

def main_application_loop():
    app = QApplication(sys.argv)
    
    while True:
        # Show login dialog
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
            
        # Create main window
        user_type = "clinic" if username == "admin" else "client"
        window = MainWindow(NODES, user_type=user_type, opcua_client=opcua_client)

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
        
        # Handle logout - use a flag to track logout state
        logout_requested = False
        
        def on_logout():
            nonlocal logout_requested
            logout_requested = True
            window.close()
            try:
                opcua_client.disconnect()
            except Exception as e:
                print(f"Logout disconnect warning: {e}")
            
        window.logout_requested.connect(on_logout)
        
        window.show()
        refresh_all()
        
        # Wait for window to close (either by logout or user closing window)
        app.exec_()
        
        # If we get here, the window was closed
        try:
            opcua_client.disconnect()
        except Exception as e:
            print(f"Window close disconnect warning: {e}")
        
        # Check if logout was requested
        if logout_requested:
            continue  # Go back to login
        else:
            break  # User closed window, exit app

if __name__ == "__main__":
    main_application_loop()