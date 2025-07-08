from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, QDateEdit, QFrame, QDialog, QLineEdit, QTextEdit, QDialogButtonBox, QDateTimeEdit
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
from node_options import CLINIC_OPTIONS, CLIENT_OPTIONS


class NodeWidget(QWidget):
    def __init__(self, node_label, node_id, node_options, user_type="clinic"):
        super().__init__()
        self.node_id = node_id
        self.layout = QHBoxLayout()
        self.label = QLabel(node_label)
        self.value_label = QLabel('N/A')

        if node_label == "Last revision date" and user_type == "clinic":
            self.input = QDateEdit()
            self.input.setCalendarPopup(True)
            self.input.setDate(QDate.currentDate())
        else:
            self.input = QComboBox()
            self.input.addItems(node_options.get(node_label, []))
            if node_label == "Last revision date":
                self.input.setEnabled(False)

        self.write_button = QPushButton('Write')
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.value_label)
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.write_button)
        self.layout.setSpacing(15)
        self.setLayout(self.layout)
        self.setMinimumWidth(500)
        # Connect Enter key or change to write button
        if isinstance(self.input, QComboBox):
            self.input.activated.connect(self.write_button.click)
        elif isinstance(self.input, QDateEdit):
            self.input.dateChanged.connect(lambda _: self.write_button.click())

    def set_value(self, value):
        self.value_label.setText(str(value))

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
        self.details_edit = QTextEdit()
        layout.addWidget(QLabel("Details:"))
        layout.addWidget(self.details_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)
    def get_data(self):
        return self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm"), self.details_edit.toPlainText()

class ViewMeetingsDialog(QDialog):
    def __init__(self, meeting_info):
        super().__init__()
        self.setWindowTitle("Scheduled Meetings")
        layout = QVBoxLayout()
        self.meeting_label = QLabel(meeting_info if meeting_info else "No meetings scheduled.")
        self.meeting_label.setWordWrap(True)
        layout.addWidget(self.meeting_label)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        self.setLayout(layout)

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
        self.logout_button = QPushButton('Logout')
        layout.addWidget(self.logout_button)
        layout.addStretch()  # Push buttons to the top
        # Username label at the bottom
        if username:
            user_label = QLabel(f"Logged in as: <b>{username}</b>")
            user_label.setAlignment(Qt.AlignCenter)
            user_label.setStyleSheet("color: #555; font-size: 12px; padding: 8px; border-top: 1px solid #ccc; margin-top: 8px;")
            layout.addWidget(user_label)
        self.setLayout(layout)

class MainWindow(QWidget):
    logout_requested = pyqtSignal()  # Signal to emit when logout is requested
    
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
                "Client name",
                "Frame integrity", 
                "Last revision date",
                "Lens condition",
                "Usage state"
            ]
            filtered_nodes = [(label, node_id) for label, node_id in nodes if label in allowed_nodes]
        
        for label, node_id in filtered_nodes:
            node_widget = NodeWidget(label, node_id, node_options, user_type=user_type)
            self.node_widgets.append(node_widget)
            content_layout.addWidget(node_widget)
            content_layout.addSpacing(5)
        
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
        self.sidebar.logout_button.clicked.connect(self.logout_requested.emit)

        # Connect schedule meeting button if client
        if user_type == "client" and hasattr(self.sidebar, "schedule_meeting_button"):
            self.sidebar.schedule_meeting_button.clicked.connect(self.open_schedule_meeting_dialog)

        # Connect view meetings button if admin
        if user_type == "clinic" and hasattr(self.sidebar, "view_meetings_button"):
            self.sidebar.view_meetings_button.clicked.connect(self.open_view_meetings_dialog)

    def open_schedule_meeting_dialog(self):
        dialog = ScheduleMeetingDialog()
        if dialog.exec_() == QDialog.Accepted:
            datetime_str, details = dialog.get_data()
            meeting_info = f"{datetime_str} | {details}"
            scheduled_meeting_nodeid = "ns=4;s=System.ScheduledMeeting"
            try:
                if self.opcua_client:
                    self.opcua_client.ensure_connected()
                    # Read current meetings array
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
        meeting_info = ""
        try:
            if self.opcua_client:
                self.opcua_client.ensure_connected()
                meetings = self.opcua_client.read_node(scheduled_meeting_nodeid)
                if isinstance(meetings, list) and meetings:
                    meeting_info = "\n\n".join(meetings)
                else:
                    meeting_info = "No meetings scheduled."
            else:
                meeting_info = "OPCUA client not available."
        except Exception as e:
            meeting_info = f"Error reading meeting info: {e}"
        dialog = ViewMeetingsDialog(meeting_info)
        dialog.exec_()

    def set_node_value(self, node_id, value):
        for widget in self.node_widgets:
            if widget.node_id == node_id:
                widget.set_value(value)

    def get_node_widgets(self):
        return self.node_widgets