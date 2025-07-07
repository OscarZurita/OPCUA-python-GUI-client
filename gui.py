from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont



class NodeWidget(QWidget):
    def __init__(self, node_label, node_id):
        super().__init__()
        self.node_id = node_id
        self.layout = QHBoxLayout()
        self.label = QLabel(node_label)
        self.value_label = QLabel('N/A')
        self.input = QLineEdit()
        self.write_button = QPushButton('Write')
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.value_label)
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.write_button)
        self.layout.setSpacing(15)
        self.setLayout(self.layout)
        self.setMinimumWidth(500)
        # Connect Enter key to write button
        self.input.returnPressed.connect(self.write_button.click)

    def set_value(self, value):
        self.value_label.setText(str(value))

class MainWindow(QWidget):
    def __init__(self, nodes):
        super().__init__()
        self.setWindowTitle('Optical clinic AAS')
        self.layout = QVBoxLayout()
        # Add main title
        self.title_label = QLabel('Optical clinic AAS')
        self.title_label.setFont(QFont('Arial', 18, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)
        self.layout.addSpacing(10)
        self.node_widgets = []
        for label, node_id in nodes:
            node_widget = NodeWidget(label, node_id)
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