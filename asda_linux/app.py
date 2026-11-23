import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QLineEdit, QGroupBox, QFormLayout
)
from .serial_link import available_ports, SerialLink
from .parameter_store import ParameterStore

STYLE = """
QMainWindow, QWidget { background:#20252b; color:#e7edf3; }
QTabWidget::pane { border:1px solid #3b4652; }
QTabBar::tab { background:#303943; padding:10px 18px; margin-right:2px; }
QTabBar::tab:selected { background:#0879bd; }
QPushButton { background:#176b9d; border:0; padding:8px 14px; border-radius:4px; }
QPushButton:hover { background:#218ac5; }
QPushButton:disabled { background:#4a535c; color:#9aa3ab; }
QLineEdit, QComboBox, QTableWidget { background:#151a1f; border:1px solid #46515c; padding:6px; }
QHeaderView::section { background:#303943; padding:6px; border:0; }
QGroupBox { border:1px solid #46515c; margin-top:10px; padding:10px; }
QGroupBox::title { subcontrol-origin:margin; left:10px; padding:0 4px; }
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASDA Soft Linux | Delta Servo Configuration")
        self.resize(1120, 720)
        self.link = SerialLink()
        self.store = ParameterStore()
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self._build_overview()
        self._build_communication()
        self._build_parameters()
        self.statusBar().showMessage("Offline — no drive commands are active")

    def _build_overview(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        title = QLabel("DELTA  /  ASDA-A2")
        title.setStyleSheet("font-size:26px;font-weight:600;color:#58b8ef;")
        subtitle = QLabel("Linux configuration and diagnostics workspace")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        box = QGroupBox("Drive profile")
        form = QFormLayout(box)
        self.model = QLineEdit("ASDA-A2")
        self.axis = QComboBox()
        self.axis.addItems(["Unassigned", "X axis", "Y axis", "Z axis", "Spindle"])
        form.addRow("Drive family", self.model)
        form.addRow("Machine axis", self.axis)
        layout.addWidget(box)
        note = QLabel(
            "Prototype status: interface and parameter-file workspace are ready. "
            "Drive communication is not activated until the exact Delta protocol "
            "and command definitions are verified."
        )
        note.setWordWrap(True)
        note.setStyleSheet("background:#303943;padding:14px;border-left:4px solid #e0a43b;")
        layout.addWidget(note)
        layout.addStretch(1)
        self.tabs.addTab(page, "Overview")

    def _build_communication(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        group = QGroupBox("Serial communication interface")
        form = QFormLayout(group)
        self.port = QComboBox()
        self.baud = QComboBox()
        self.baud.addItems(["9600", "19200", "38400", "57600", "115200"])
        refresh = QPushButton("Refresh ports")
        refresh.clicked.connect(self.refresh_ports)
        portrow = QHBoxLayout()
        portrow.addWidget(self.port, 1)
        portrow.addWidget(refresh)
        form.addRow("Device", portrow)
        form.addRow("Baud rate", self.baud)
        layout.addWidget(group)
        buttons = QHBoxLayout()
        self.connect_btn = QPushButton("Open serial port")
        self.disconnect_btn = QPushButton("Close port")
        self.disconnect_btn.setEnabled(False)
        self.connect_btn.clicked.connect(self.connect_port)
        self.disconnect_btn.clicked.connect(self.disconnect_port)
        buttons.addWidget(self.connect_btn)
        buttons.addWidget(self.disconnect_btn)
        buttons.addStretch(1)
        layout.addLayout(buttons)
        self.comm_state = QLabel("Not connected")
        self.comm_state.setStyleSheet("font-size:16px;padding:12px;")
        layout.addWidget(self.comm_state)
        safety = QLabel(
            "Opening a serial port only checks that Linux can access the adapter. "
            "This version sends no bytes to the servo drive."
        )
        safety.setWordWrap(True)
        layout.addWidget(safety)
        layout.addStretch(1)
        self.tabs.addTab(page, "Communication")
        self.refresh_ports()

    def refresh_ports(self):
        current = self.port.currentData() if hasattr(self, "port") else None
        self.port.clear()
        for p in available_ports():
            self.port.addItem(f"{p.device} — {p.description}", p.device)
        if current:
            idx = self.port.findData(current)
            if idx >= 0:
                self.port.setCurrentIndex(idx)
        if self.port.count() == 0:
            self.port.addItem("No serial ports detected", "")

    def connect_port(self):
        device = self.port.currentData()
        if not device:
            QMessageBox.warning(self, "Serial", "No serial port selected.")
            return
        try:
            self.link.open(device, int(self.baud.currentText()))
            self.comm_state.setText(f"Port open: {device} @ {self.baud.currentText()} baud")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.statusBar().showMessage("Serial adapter open — protocol not yet enabled")
        except Exception as exc:
            QMessageBox.critical(self, "Connection error", str(exc))

    def disconnect_port(self):
        self.link.close()
        self.comm_state.setText("Not connected")
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.statusBar().showMessage("Offline")

    def _build_parameters(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        bar = QHBoxLayout()
        add = QPushButton("Add documented parameter")
        load = QPushButton("Import JSON/CSV")
        save = QPushButton("Export JSON/CSV")
        add.clicked.connect(self.add_parameter)
        load.clicked.connect(self.import_parameters)
        save.clicked.connect(self.export_parameters)
        for b in (add, load, save):
            bar.addWidget(b)
        bar.addStretch(1)
        layout.addLayout(bar)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Parameter", "Name", "Value", "Unit", "Description"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.tabs.addTab(page, "Parameters")

    def add_parameter(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col in range(5):
            self.table.setItem(row, col, QTableWidgetItem(""))

    def import_parameters(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import parameter list", "", "Parameter files (*.json *.csv)")
        if not path:
            return
        try:
            if path.lower().endswith(".json"):
                self.store.load_json(path)
            else:
                self.store.load_csv(path)
            self.table.setRowCount(0)
            keys = ["parameter", "name", "value", "unit", "description"]
            for record in self.store.rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                for col, key in enumerate(keys):
                    self.table.setItem(row, col, QTableWidgetItem(str(record.get(key, ""))))
        except Exception as exc:
            QMessageBox.critical(self, "Import error", str(exc))

    def export_parameters(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export parameter list", "asda_parameters.json",
            "JSON (*.json);;CSV (*.csv)")
        if not path:
            return
        keys = ["parameter", "name", "value", "unit", "description"]
        records = []
        for row in range(self.table.rowCount()):
            records.append({key: (self.table.item(row, col).text()
                           if self.table.item(row, col) else "")
                           for col, key in enumerate(keys)})
        self.store.rows = records
        try:
            if path.lower().endswith(".csv"):
                self.store.save_csv(path)
            else:
                if not path.lower().endswith(".json"):
                    path += ".json"
                self.store.save_json(path)
            self.statusBar().showMessage(f"Exported {len(records)} records")
        except Exception as exc:
            QMessageBox.critical(self, "Export error", str(exc))

    def closeEvent(self, event):
        self.link.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    return app.exec()
