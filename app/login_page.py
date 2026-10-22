"""
Login Page for RehabQuest
-------------------------
Sign-in screen supporting one-click Demo Patient access as well as
custom patient ID registration.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QLinearGradient, QColor

from auth import login as db_login, register as db_register, AuthError


class LoginPage(QWidget):
    login_requested = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#31215C"))
        gradient.setColorAt(0.6, QColor("#4A328C"))
        gradient.setColorAt(1.0, QColor("#6B4FD1"))
        painter.fillRect(self.rect(), gradient)
        super().paintEvent(event)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setFixedSize(380, 460)
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 245);
                border-radius: 24px;
            }
        """)
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(32, 32, 32, 28)
        c_layout.setSpacing(10)

        # Brand header
        brand_row = QHBoxLayout()
        logo = QLabel("\u2695\ufe0f")
        logo.setStyleSheet("font-size: 26px; background: transparent;")
        brand_row.addWidget(logo)

        brand_lbl = QLabel("REHABQUEST")
        b_font = QFont("Segoe UI", 16)
        b_font.setWeight(QFont.Weight.Bold)
        b_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.4)
        brand_lbl.setFont(b_font)
        brand_lbl.setStyleSheet("color: #2F2154; background: transparent;")
        brand_row.addWidget(brand_lbl)
        brand_row.addStretch()
        c_layout.addLayout(brand_row)

        sub = QLabel("Gamified Clinical Kinematics & Motor Recovery")
        sub.setStyleSheet("color: #7A6C9B; font-size: 11px; background: transparent;")
        c_layout.addWidget(sub)
        c_layout.addSpacing(10)

        # Quick Demo Button
        demo_btn = QPushButton("\u26a1 Quick Start as Demo Patient")
        demo_btn.setFixedHeight(42)
        demo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        demo_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7E5BE8, stop:1 #A878E0);
                color: #FFFFFF;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8E6BF8, stop:1 #B888F0);
            }
        """)
        demo_btn.clicked.connect(self._login_demo)
        c_layout.addWidget(demo_btn)

        # Divider
        div_row = QHBoxLayout()
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setStyleSheet("color: rgba(133, 103, 232, 40);")
        div_lbl = QLabel("or enter Patient ID")
        div_lbl.setStyleSheet("color: #9C8FB8; font-size: 10px; background: transparent;")
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("color: rgba(133, 103, 232, 40);")
        div_row.addWidget(line1)
        div_row.addWidget(div_lbl)
        div_row.addWidget(line2)
        c_layout.addLayout(div_row)

        # Input fields
        c_layout.addWidget(QLabel("Patient ID", styleSheet="color: #4C397A; font-size: 11px; font-weight: bold; background: transparent;"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("e.g. PATIENT_01")
        self.id_input.setFixedHeight(38)
        self.id_input.setStyleSheet("""
            QLineEdit {
                background-color: #F4F1FA;
                border: 1px solid #D6CCEE;
                border-radius: 10px;
                padding: 0 12px;
                color: #2F2154;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #7E5BE8;
            }
        """)
        c_layout.addWidget(self.id_input)

        c_layout.addWidget(QLabel("Patient Name", styleSheet="color: #4C397A; font-size: 11px; font-weight: bold; background: transparent;"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Alex Mercer")
        self.name_input.setFixedHeight(38)
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #F4F1FA;
                border: 1px solid #D6CCEE;
                border-radius: 10px;
                padding: 0 12px;
                color: #2F2154;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #7E5BE8;
            }
        """)
        c_layout.addWidget(self.name_input)

        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet("color: #E53E3E; font-size: 11px; background: transparent;")
        c_layout.addWidget(self.error_lbl)

        c_layout.addStretch()

        sign_in_btn = QPushButton("Access Portal")
        sign_in_btn.setFixedHeight(40)
        sign_in_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        sign_in_btn.setStyleSheet("""
            QPushButton {
                background-color: #F1ECFC;
                color: #6546C9;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid rgba(126, 91, 232, 60);
            }
            QPushButton:hover {
                background-color: #E6DCFA;
            }
        """)
        sign_in_btn.clicked.connect(self._login_custom)
        c_layout.addWidget(sign_in_btn)

        main_layout.addWidget(card)

    def _login_demo(self):
        self.login_requested.emit("PATIENT_01", "Alex Mercer")

    def _login_custom(self):
        pid = self.id_input.text().strip()
        pname = self.name_input.text().strip()
        if not pid:
            self.error_lbl.setText("Please enter a Patient ID.")
            return
        user = db_register(pid, pname)
        self.login_requested.emit(user["user_id"], user["name"])

