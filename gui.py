from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, QDateEdit, QFrame, QDialog, QLineEdit, QTextEdit, QDialogButtonBox, QDateTimeEdit, QScrollArea
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
from node_options import CLINIC_OPTIONS, CLIENT_OPTIONS


class NodeWidget(QWidget):
    def __init__(self, node_label, node_id, node_options, user_type="clinic", client_name=None):
        super().__init__()
        self.node_id = node_id
        self.client_name = client_name  # Save the client name for later use
        self.layout = QHBoxLayout()
        self.label = QLabel(node_label)

        if node_label == "LastRevisionDate" and user_type == "clinic":
            self.value_label = QLabel('N/A')
            self.input = QDateEdit(calendarPopup=True)
            self.input.setDate(QDate.currentDate())
        elif user_type == "clinic":
            self.value_label = QLabel('N/A')
            self.input = QComboBox()
            self.input.addItems(node_options.get(node_label, []))
        else:
            # For clients, show only one label as value (no value_label)
            if node_label == "ClientName" and client_name is not None:
                self.input = QLabel(client_name)
            else:
                self.input = QLabel("")
            self.input.setStyleSheet("background: #f5f5f5; border: 1px solid #ccc; padding: 4px;")
            self.input.setMinimumWidth(120)
            self.value_label = None  # No value_label for clients

        self.layout.addWidget(self.label)
        if self.value_label is not None:
            self.layout.addWidget(self.value_label)
        self.layout.addWidget(self.input)

        # Only show the Write button for clinic (admin)
        if user_type == "clinic":
            self.write_button = QPushButton('Write')
            self.layout.addWidget(self.write_button)
        else:
            self.write_button = None  # For consistency

        self.layout.setSpacing(15)
        self.setLayout(self.layout)
        self.setMinimumWidth(500)
        # Connect Enter key or change to write button
        if self.write_button is not None:
            if isinstance(self.input, QComboBox):
                self.input.activated.connect(self.write_button.click)
            elif isinstance(self.input, QDateEdit):
                self.input.dateChanged.connect(lambda _: self.write_button.click())

    def set_value(self, value):
        # Standard display for all users
        if value is None or value == "" or (isinstance(value, list) and not value):
            display_value = ""
        else:
            display_value = str(value)
        if self.value_label is not None:
            self.value_label.setText(display_value)
        if isinstance(self.input, QLabel):
            self.input.setText(display_value)

class ScheduleMeetingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Schedule Meeting")
        layout = QVBoxLayout()
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDateTime(QDate.currentDate().startOfDay())
        layout.addWidget(QLabel("Select date and time:"))
        layout.addWidget(self.datetime_edit)

        # Add meeting type combo box
        layout.addWidget(QLabel("Meeting type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Revision", "Maintenance"])
        layout.addWidget(self.type_combo)

        self.details_edit = QTextEdit()
        layout.addWidget(QLabel("Details:"))
        layout.addWidget(self.details_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_data(self):
        return (
            self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm"),
            self.type_combo.currentText(),
            self.details_edit.toPlainText()
        )

class ViewMeetingsDialog(QDialog):
    def __init__(self, meetings, parent):
        super().__init__(parent)
        self.setWindowTitle("Scheduled Meetings")
        self.opcua_client = parent.opcua_client
        self.meetings = meetings
        
        layout = QVBoxLayout()
        
        if not meetings:
            layout.addWidget(QLabel("No meetings scheduled."))
        else:
            for i, meeting in enumerate(self.meetings):
                meeting_layout = QHBoxLayout()
                
                label = QLabel(meeting)
                label.setWordWrap(True)
                meeting_layout.addWidget(label)
                
                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda _, m=meeting: self.delete_meeting(m))
                meeting_layout.addWidget(delete_button)
                
                layout.addLayout(meeting_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

    def delete_meeting(self, meeting_to_delete):
        self.meetings.remove(meeting_to_delete)
        
        scheduled_meeting_nodeid = "ns=4;s=System.ScheduledMeeting"
        try:
            if self.opcua_client:
                self.opcua_client.ensure_connected()
                self.opcua_client.write_node(scheduled_meeting_nodeid, self.meetings)
                print(f"Meeting deleted and updated in OPC UA: {meeting_to_delete}")
                self.accept()  # Close and reopen to refresh
            else:
                print("OPCUA client not available, could not delete meeting.")
        except Exception as e:
            print(f"Error deleting meeting: {e}")


class Sidebar(QWidget):
    def __init__(self, user_type="clinico", username=None):
        super().__init__()
        layout = QVBoxLayout()
        # Title label
        if user_type == "client":
            title = QLabel("Client")
        else:
            title = QLabel("Admin")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(title)
        layout.addSpacing(10)
        if user_type == "client":
            self.schedule_meeting_button = QPushButton("Schedule Meeting")
            layout.addWidget(self.schedule_meeting_button)
        else:
            self.view_meetings_button = QPushButton("View Meetings")
            layout.addWidget(self.view_meetings_button)
            
        self.logout_button = QPushButton("Logout")
        layout.addWidget(self.logout_button)
        layout.addStretch()  # Push buttons to the top
        # Username label at the bottom
        if username:
            if user_type == "clinic":
                user_label = QLabel(f"Logged in as: <b>admin</b>")
            else:
                user_label = QLabel(f"Logged in as: <b>{username}</b>")
            user_label.setAlignment(Qt.AlignCenter)
            user_label.setStyleSheet("color: #555; font-size: 12px; padding: 8px; border-top: 1px solid #ccc; margin-top: 8px;")
            layout.addWidget(user_label)
        self.setLayout(layout)

class MainWindow(QWidget):
    logout_requested = pyqtSignal()
    
    def __init__(self, nodes, user_type="clinico", opcua_client=None, username=None):
        super().__init__()
        self.setWindowTitle('Optical clinic AAS')
        self.opcua_client = opcua_client
        main_layout = QHBoxLayout()  # Main layout is now horizontal

        # Sidebar
        self.sidebar = Sidebar(user_type=user_type, username=username)
        main_layout.addWidget(self.sidebar)
        self.sidebar.setFixedWidth(200)
        # Add a vertical line separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        self.title_label = QLabel('Optical clinic AAS')
        self.title_label.setFont(QFont('Arial', 18, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.title_label)
        content_layout.addSpacing(10)
        self.node_widgets = []
        
        # Define which nodes to show based on user type
        if user_type == "clinic":
            node_options = CLINIC_OPTIONS
            # Show all nodes for clinic users
            filtered_nodes = nodes
        else:
            node_options = CLIENT_OPTIONS
            # Show only specific nodes for client users
            allowed_nodes = [
                "ClientName",
                "FrameIntegrity",
                "LastRevisionDate",
                "LensCondition",
                "UsageState"
            ]
            filtered_nodes = [(label, node_id) for label, node_id in nodes if label in allowed_nodes]
        
        for label, node_id in filtered_nodes:
            node_widget = NodeWidget(label, node_id, node_options, user_type=user_type, client_name=username)
            self.node_widgets.append(node_widget)
            content_layout.addWidget(node_widget)
            content_layout.addSpacing(5)
            # Connect Write button if it exists
            if hasattr(node_widget, "write_button") and node_widget.write_button is not None:
                node_widget.write_button.clicked.connect(lambda _, w=node_widget: self.handle_write(w))

        # Add buttons layout (only refresh here)
        buttons_layout = QHBoxLayout()
        self.refresh_button = QPushButton('Refresh All')
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addStretch()
        content_layout.addSpacing(10)
        content_layout.addLayout(buttons_layout)
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)
        self.setMinimumWidth(600)
        
        # Connect logout button from sidebar
        self.sidebar.logout_button.clicked.connect(self.handle_logout)

        # Connect schedule meeting button if client
        if user_type == "client" and hasattr(self.sidebar, "schedule_meeting_button"):
            self.sidebar.schedule_meeting_button.clicked.connect(self.open_schedule_meeting_dialog)

        # Connect view meetings button if admin
        if user_type == "clinic":
            if hasattr(self.sidebar, "view_meetings_button"):
                self.sidebar.view_meetings_button.clicked.connect(self.open_view_meetings_dialog)

    def open_schedule_meeting_dialog(self):
        dialog = ScheduleMeetingDialog()
        if dialog.exec_() == QDialog.Accepted:
            datetime_str, meeting_type, details = dialog.get_data()
            meeting_info = f"{datetime_str} | {meeting_type} | {details}"
            scheduled_meeting_nodeid = "ns=4;s=System.ScheduledMeeting"
            try:
                if self.opcua_client:
                    self.opcua_client.ensure_connected()
                    meetings = self.opcua_client.read_node(scheduled_meeting_nodeid)
                    if not isinstance(meetings, list):
                        meetings = []
                    meetings.append(meeting_info)
                    self.opcua_client.ensure_connected()
                    self.opcua_client.write_node(scheduled_meeting_nodeid, meetings)
                    print(f"Meeting scheduled and written to OPC UA: {meeting_info}")
                else:
                    print("OPCUA client not available, could not write meeting info.")
            except Exception as e:
                print(f"Error writing meeting info: {e}")

    def open_view_meetings_dialog(self):
        scheduled_meeting_nodeid = "ns=4;s=System.ScheduledMeeting"
        meetings = []
        try:
            if self.opcua_client:
                self.opcua_client.ensure_connected()
                meetings = self.opcua_client.read_node(scheduled_meeting_nodeid)
                if not isinstance(meetings, list):
                    meetings = []
            else:
                print("OPCUA client not available.")
        except Exception as e:
            print(f"Error reading meeting info: {e}")
        
        dialog = ViewMeetingsDialog(meetings, self)
        dialog.exec_()


    def set_node_value(self, node_id, value):
        for widget in self.node_widgets:
            if widget.node_id == node_id:
                widget.set_value(value)

    def get_node_widgets(self):
        return self.node_widgets

    def set_client_name(self, client_name):
        for widget in self.node_widgets:
            if widget.label.text() == "ClientName":
                if hasattr(widget.input, "setCurrentText"):
                    widget.input.setCurrentText(client_name)
                if widget.value_label is not None:
                    widget.value_label.setText(client_name)
                if hasattr(widget.input, "setEnabled"):
                    widget.input.setEnabled(False)

    def handle_logout(self):
        self.logout_requested.emit()
        self.close()

    def handle_write(self, node_widget):
        value = None
        # Get value from input
        if isinstance(node_widget.input, QComboBox):
            value = node_widget.input.currentText()
        elif isinstance(node_widget.input, QDateEdit):
            value = node_widget.input.date().toString("yyyy-MM-dd")
        else:
            return  # Not editable

        try:
            if self.opcua_client:
                self.opcua_client.ensure_connected()
                self.opcua_client.write_node(node_widget.node_id, value)
                node_widget.set_value(value)
        except Exception as e:
            print(f"Error writing value: {e}")

