from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, QDateEdit
from PyQt5.QtCore import Qt, QDate
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

class MainWindow(QWidget):
    def __init__(self, nodes, user_type="clinico"):
        super().__init__()
        self.setWindowTitle('Optical clinic AAS')
        self.layout = QVBoxLayout()
        self.title_label = QLabel('Optical clinic AAS')
        self.title_label.setFont(QFont('Arial', 18, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)
        self.layout.addSpacing(10)
        self.node_widgets = []
        if user_type == "clinic":
            node_options = CLINIC_OPTIONS
        else:
            node_options = CLIENT_OPTIONS
        for label, node_id in nodes:
            node_widget = NodeWidget(label, node_id, node_options, user_type=user_type)
            self.node_widgets.append(node_widget)
            self.layout.addWidget(node_widget)
            self.layout.addSpacing(5)
        self.refresh_button = QPushButton('Refresh All')
        self.layout.addSpacing(10)
        self.layout.addWidget(self.refresh_button)
        self.setLayout(self.layout)
        self.setMinimumWidth(600)

    def set_node_value(self, node_id, value):
        for widget in self.node_widgets:
            if widget.node_id == node_id:
                widget.set_value(value)

    def get_node_widgets(self):
        return self.node_widgets