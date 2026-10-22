
"""
Login Page for RehabQuest
-------------------------
Sign-in screen supporting Demo Patient access and custom patient
registration using the existing authentication module.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import (
    QFont,
    QPainter,
    QLinearGradient,
    QColor,
)

from auth import login as db_login, register as db_register, AuthError


class LoginPage(QWidget):

    login_requested = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        gradient = QLinearGradient(
            0, 0, self.width(), self.height()
        )
        gradient.setColorAt(0.0, QColor("#31215C"))
        gradient.setColorAt(0.6, QColor("#4A328C"))
        gradient.setColorAt(1.0, QColor("#6B4FD1"))

        painter.fillRect(self.rect(), gradient)
        painter.end()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # Main login card
        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedSize(380, 460)

        card.setStyleSheet("""
            QFrame#loginCard {
                background-color: rgba(255, 255, 255, 245);
                border-radius: 24px;
                border: none;
            }

            QLabel {
                background: transparent;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 28, 32, 24)
        card_layout.setSpacing(9)

        # Brand header
        brand_row = QHBoxLayout()
        brand_row.setSpacing(8)

        logo = QLabel("⚕️")
        logo.setStyleSheet(
            "font-size: 26px; background: transparent;"
        )
        brand_row.addWidget(logo)

        brand_label = QLabel("REHABQUEST")

        brand_font = QFont("Segoe UI", 16)
        brand_font.setWeight(QFont.Weight.Bold)
        brand_font.setLetterSpacing(
            QFont.SpacingType.AbsoluteSpacing, 1.4
        )

        brand_label.setFont(brand_font)
        brand_label.setStyleSheet(
            "color: #2F2154; background: transparent;"
        )

        brand_row.addWidget(brand_label)
        brand_row.addStretch()
        card_layout.addLayout(brand_row)

        subtitle = QLabel(
            "Gamified Clinical Kinematics & Motor Recovery"
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            "color: #7A6C9B; font-size: 11px;"
        )
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(8)

        # Demo access
        self.demo_btn = QPushButton(
            "⚡ Quick Start as Demo Patient"
        )
        self.demo_btn.setFixedHeight(42)
        self.demo_btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.demo_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7E5BE8, stop:1 #A878E0
                );
                color: #FFFFFF;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                border: none;
            }

            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8E6BF8, stop:1 #B888F0
                );
            }

            QPushButton:disabled {
                background-color: #B9A9E8;
            }
        """)

        self.demo_btn.clicked.connect(self._login_demo)
        card_layout.addWidget(self.demo_btn)

        # Divider
        divider_row = QHBoxLayout()
        divider_row.setSpacing(8)

        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setStyleSheet(
            "color: rgba(133, 103, 232, 60);"
        )

        divider_label = QLabel("or enter Patient ID")
        divider_label.setStyleSheet(
            "color: #9C8FB8; font-size: 10px;"
        )

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet(
            "color: rgba(133, 103, 232, 60);"
        )

        divider_row.addWidget(line1, 1)
        divider_row.addWidget(divider_label)
        divider_row.addWidget(line2, 1)

        card_layout.addLayout(divider_row)

        # Patient ID
        patient_id_label = QLabel("Patient ID")
        patient_id_label.setStyleSheet(
            "color: #4C397A; font-size: 11px; "
            "font-weight: bold;"
        )
        card_layout.addWidget(patient_id_label)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("e.g. PATIENT_01")
        self.id_input.setFixedHeight(38)
        self.id_input.setMaxLength(64)
        self.id_input.setStyleSheet(
            self._input_style()
        )
        self.id_input.returnPressed.connect(
            self._login_custom
        )
        card_layout.addWidget(self.id_input)

        # Patient name
        patient_name_label = QLabel("Patient Name")
        patient_name_label.setStyleSheet(
            "color: #4C397A; font-size: 11px; "
            "font-weight: bold;"
        )
        card_layout.addWidget(patient_name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Alex Mercer")
        self.name_input.setFixedHeight(38)
        self.name_input.setMaxLength(100)
        self.name_input.setStyleSheet(
            self._input_style()
        )
        self.name_input.returnPressed.connect(
            self._login_custom
        )
        card_layout.addWidget(self.name_input)

        # Error and status message
        self.error_lbl = QLabel("")
        self.error_lbl.setWordWrap(True)
        self.error_lbl.setMinimumHeight(16)
        self.error_lbl.setStyleSheet(
            "color: #E53E3E; font-size: 10px;"
        )
        card_layout.addWidget(self.error_lbl)

        card_layout.addStretch()

        # Sign-in button
        self.sign_in_btn = QPushButton("Access Portal")
        self.sign_in_btn.setFixedHeight(40)
        self.sign_in_btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.sign_in_btn.setStyleSheet("""
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

            QPushButton:disabled {
                color: #9C8FB8;
            }
        """)

        self.sign_in_btn.clicked.connect(
            self._login_custom
        )
        card_layout.addWidget(self.sign_in_btn)

        main_layout.addWidget(card)

    @staticmethod
    def _input_style():
        return """
            QLineEdit {
                background-color: #F4F1FA;
                border: 1px solid #D6CCEE;
                border-radius: 10px;
                padding: 0 12px;
                color: #2F2154;
                font-size: 12px;
                selection-background-color: #7E5BE8;
            }

            QLineEdit:focus {
                border: 1px solid #7E5BE8;
            }
        """

    def _show_error(self, message):
        self.error_lbl.setStyleSheet(
            "color: #E53E3E; font-size: 10px;"
        )
        self.error_lbl.setText(message)

    def _login_demo(self):
        """Open the predefined demo patient."""
        self.error_lbl.clear()

        self.login_requested.emit(
            "PATIENT_01",
            "Alex Mercer",
        )

    def _login_custom(self):
        """Register or access a patient using the existing auth API."""
        patient_id = self.id_input.text().strip()
        patient_name = self.name_input.text().strip()

        self.error_lbl.clear()

        if not patient_id:
            self._show_error(
                "Please enter a Patient ID."
            )
            self.id_input.setFocus()
            return

        if not patient_name:
            self._show_error(
                "Please enter a Patient Name."
            )
            self.name_input.setFocus()
            return

        try:
            # Preserve the existing registration workflow.
            user = db_register(
                patient_id,
                patient_name,
            )

            if not user:
                self._show_error(
                    "Registration did not return a user."
                )
                return

            user_id = user.get("user_id")
            name = user.get("name")

            if not user_id or not name:
                self._show_error(
                    "The authentication service returned "
                    "incomplete patient information."
                )
                return

            self.login_requested.emit(
                str(user_id),
                str(name),
            )

        except AuthError as exc:
            self._show_error(str(exc))

        except Exception:
            # Avoid showing internal database details to users.
            self._show_error(
                "Unable to access the patient account. "
                "Please check your details and try again."
            )
