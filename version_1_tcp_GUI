import sys
import socket
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import QTimer


class RainSystemControl(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rain System Control - Python ↔ LabVIEW")

        # --- Widgets
        self.flow_label = QLabel("Set Flow Rate (L/min):")
        self.flow_input = QLineEdit()
        self.start_button = QPushButton("Start Rain System")
        self.stop_button = QPushButton("Stop Rain System")
        self.status_label = QLabel("System Status: OFF")
        self.sensor_label = QLabel("Current Flow: -- L/min")

        # --- Layout
        layout = QVBoxLayout()
        layout.addWidget(self.flow_label)
        layout.addWidget(self.flow_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.sensor_label)
        self.setLayout(layout)

        # --- Signals
        self.start_button.clicked.connect(self.start_rain)
        self.stop_button.clicked.connect(self.stop_rain)

        # --- Timer for polling sensor feedback
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_sensor)
        self.timer.start(2000)  # every 2 seconds

    def send_tcp(self, command_dict):
        HOST = '127.0.0.1'
        PORT = 5025
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                msg = json.dumps(command_dict).encode()
                s.sendall(msg)
                response = s.recv(1024)
                return json.loads(response.decode())
        except Exception as e:
            print(f"[TCP Error] {e}")
            return {}

    def start_rain(self):
        try:
            flow_rate = float(self.flow_input.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Enter a valid flow rate.")
            return

        feedback = self.send_tcp({"command": "start", "flow_rate": flow_rate})
        self.status_label.setText("System Status: RUNNING")
        if "current_flow" in feedback:
            self.sensor_label.setText(f"Current Flow: {feedback['current_flow']} L/min")

    def stop_rain(self):
        feedback = self.send_tcp({"command": "stop"})
        self.status_label.setText("System Status: STOPPED")
        if "current_flow" in feedback:
            self.sensor_label.setText(f"Current Flow: {feedback['current_flow']} L/min")

    def poll_sensor(self):
        feedback = self.send_tcp({})
        if "current_flow" in feedback:
            self.sensor_label.setText(f"[LIVE] Current Flow: {feedback['current_flow']} L/min")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = RainSystemControl()
    gui.show()
    sys.exit(app.exec_())
