from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('OPC UA Client')
        self.layout = QVBoxLayout()
        self.value_label = QLabel('Value: N/A')
        self.refresh_button = QPushButton('Refresh')
        self.layout.addWidget(self.value_label)
        self.layout.addWidget(self.refresh_button)
        self.setLayout(self.layout)

    def set_value(self, value):
        self.value_label.setText(f'Value: {value}') 