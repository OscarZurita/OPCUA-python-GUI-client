from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox

class SelectClientDialog(QDialog):
    def __init__(self, client_names):
        super().__init__()
        self.setWindowTitle("Select a client")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Clients:"))
        self.combo = QComboBox()
        self.combo.addItems(client_names)
        layout.addWidget(self.combo)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_selected_client(self):
        return self.combo.currentText()