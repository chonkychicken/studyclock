import sys
import time
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import QTimer, Qt

class Stopwatch(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stopwatch")

        # State
        self.elapsed = 0
        self.total_elapsed = 0   # ✅ NEW: running total
        self.running = False
        self.direction = 1
        self.last_update = time.perf_counter()

        self.current_color = "white"
        self.last_display = ""
        self.always_on_top = False

        # UI
        self.label = QLabel("00:00")
        self.label.setStyleSheet("color: white; font-size: 40px;")

        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.reset_btn = QPushButton("Reset")
        self.mode_btn = QPushButton("Mode: Studying 📖📖")

        self.top_btn = QPushButton("📌 Off")
        self.top_btn.setFixedWidth(60)

        main_layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        top_bar.addStretch()
        top_bar.addWidget(self.top_btn)

        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.start_btn)
        main_layout.addWidget(self.stop_btn)
        main_layout.addWidget(self.reset_btn)
        main_layout.addWidget(self.mode_btn)

        self.setLayout(main_layout)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(10)

        # Connections
        self.start_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.reset_btn.clicked.connect(self.reset)
        self.mode_btn.clicked.connect(self.toggle_mode)
        self.top_btn.clicked.connect(self.toggle_always_on_top)

    def format_hms(self, t):
        """Always HH:MM:SS (used for saving)"""
        hours = int(t // 3600)
        mins = int((t % 3600) // 60)
        secs = int(t % 60)
        return f"{hours:02}:{mins:02}:{secs:02}"

    def format_display(self, t, sign=""):
        """Dynamic display"""
        if t < 3600:
            mins = int(t // 60)
            secs = int(t % 60)
            return f"{sign}{mins:02}:{secs:02}"
        else:
            return f"{sign}{self.format_hms(t)}"

    def update_time(self):
        now = time.perf_counter()

        if self.running:
            delta = now - self.last_update
            self.elapsed += self.direction * delta

        self.last_update = now

        # Color + sign
        if self.elapsed > 0:
            new_color = "#8DD06C"
            sign = ""
        elif self.elapsed < 0:
            new_color = "#CC0202"
            sign = "-"
        else:
            new_color = "white"
            sign = ""

        if new_color != self.current_color:
            self.label.setStyleSheet(f"color: {new_color}; font-size: 40px;")
            self.current_color = new_color

        t = abs(self.elapsed)
        time_str = self.format_display(t, sign)

        if time_str != self.last_display:
            self.label.setText(time_str)
            self.last_display = time_str

    def start(self):
        if not self.running:
            self.last_update = time.perf_counter()
            self.running = True

    def stop(self):
        self.running = False

    def save_session(self):
        t = abs(self.elapsed)

        # ✅ Add to running total
        self.total_elapsed += t

        delta_str = self.format_hms(t)
        total_str = self.format_hms(self.total_elapsed)

        mode = "Studying" if self.direction == 1 else "Break"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("sessions.txt", "a") as f:
            f.write(f"[{timestamp}] {mode} | Δ: {delta_str} | Total: {total_str}\n")

    def reset(self):
        if self.elapsed != 0:
            self.save_session()

        self.running = False
        self.elapsed = 0
        self.label.setText("00:00")
        self.last_display = "00:00"

    def toggle_mode(self):
        self.direction *= -1

        if self.direction == 1:
            self.mode_btn.setText("Mode: Studying 📖📖")
        else:
            self.mode_btn.setText("Mode: On Break 😴😴")

    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top

        if self.always_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            self.top_btn.setText("📌 On")
        else:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
            self.top_btn.setText("📌 Off")

        self.show() 


app = QApplication(sys.argv)
window = Stopwatch()
window.show()
sys.exit(app.exec())