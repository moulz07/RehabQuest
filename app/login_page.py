
"""
Login Page for RehabQuest
-------------------------
Provides Sign In, Sign Up, and Demo Patient access
using the existing local authentication module.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QStackedWidget,
    QSizePolicy,
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
        painter.end()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Main card
        self.card = QFrame()
        self.card.setObjectName("loginCard")
        self.card.setMaximumWidth(520)
        self.card.setMinimumWidth(420)
        self.card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        self.card.setStyleSheet("""
            QFrame#loginCard {
                background-color: rgba(255, 255, 255, 248);
                border-radius: 24px;
                border: none;
            }

            QLabel {
                background: transparent;
            }
        """)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(36, 28, 36, 28)
        card_layout.setSpacing(12)

        # Brand header
        brand_row = QHBoxLayout()
        brand_row.setSpacing(10)

        logo = QLabel("⚕")
        logo.setStyleSheet(
            "font-size: 30px; color: #4C8DFF; background: transparent;"
        )
        brand_row.addWidget(logo)

        brand_label = QLabel("REHABQUEST")
        brand_font = QFont("Segoe UI", 21)
        brand_font.setWeight(QFont.Weight.Bold)
        brand_font.setLetterSpacing(
            QFont.SpacingType.AbsoluteSpacing, 1.5
        )
        brand_label.setFont(brand_font)
        brand_label.setStyleSheet("color: #2F2154;")

        brand_row.addWidget(brand_label)
        brand_row.addStretch()
        card_layout.addLayout(brand_row)

        subtitle = QLabel(
            "Gamified Clinical Kinematics & Motor Recovery"
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #7A6C9B; font-size: 12px;")
        card_layout.addWidget(subtitle)

        # Sign In / Sign Up tabs
        tabs = QHBoxLayout()
        tabs.setSpacing(8)

        self.signin_tab = QPushButton("Sign In")
        self.signup_tab = QPushButton("Create Account")

        for button in (self.signin_tab, self.signup_tab):
            button.setFixedHeight(40)
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.signin_tab.clicked.connect(
            lambda: self._set_mode("signin")
        )
        self.signup_tab.clicked.connect(
            lambda: self._set_mode("signup")
        )

        tabs.addWidget(self.signin_tab)
        tabs.addWidget(self.signup_tab)
        card_layout.addLayout(tabs)

        # Form pages
        self.pages = QStackedWidget()
        card_layout.addWidget(self.pages)

        self._build_signin_page()
        self._build_signup_page()

        self._set_mode("signin")

        main_layout.addWidget(self.card)

    # ---------------------------------------------------------
    # Sign In
    # ---------------------------------------------------------

    def _build_signin_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(9)

        heading = QLabel("Welcome back!")
        heading.setStyleSheet(
            "color: #35245F; font-size: 20px; font-weight: bold;"
        )
        layout.addWidget(heading)

        hint = QLabel(
            "Sign in to continue to your rehabilitation dashboard."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #85799D; font-size: 11px;")
        layout.addWidget(hint)

        layout.addWidget(self._field_label("Patient ID"))

        self.signin_id = QLineEdit()
        self.signin_id.setPlaceholderText("Enter your Patient ID")
        self._style_input(self.signin_id)
        self.signin_id.returnPressed.connect(self._signin)
        layout.addWidget(self.signin_id)

        layout.addWidget(self._field_label("Password"))

        self.signin_password = QLineEdit()
        self.signin_password.setPlaceholderText("Enter your password")
        self.signin_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._style_input(self.signin_password)
        self.signin_password.returnPressed.connect(self._signin)
        layout.addWidget(self.signin_password)

        self.signin_error = self._error_label()
        layout.addWidget(self.signin_error)

        self.signin_button = QPushButton("Sign In")
        self.signin_button.setFixedHeight(44)
        self.signin_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.signin_button.setStyleSheet(self._primary_button_style())
        self.signin_button.clicked.connect(self._signin)
        layout.addWidget(self.signin_button)

        # Demo access
        self.demo_btn = QPushButton(
            "⚡  Continue as Demo Patient"
        )
        self.demo_btn.setFixedHeight(42)
        self.demo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.demo_btn.setStyleSheet(self._secondary_button_style())
        self.demo_btn.clicked.connect(self._login_demo)
        layout.addWidget(self.demo_btn)

        layout.addStretch()
        self.pages.addWidget(page)

    # ---------------------------------------------------------
    # Sign Up
    # ---------------------------------------------------------

    def _build_signup_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(7)

        heading = QLabel("Create your account")
        heading.setStyleSheet(
            "color: #35245F; font-size: 20px; font-weight: bold;"
        )
        layout.addWidget(heading)

        hint = QLabel(
            "Create a local profile to save your RehabQuest sessions."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #85799D; font-size: 11px;")
        layout.addWidget(hint)

        layout.addWidget(self._field_label("Full Name"))

        self.signup_name = QLineEdit()
        self.signup_name.setPlaceholderText("Enter your full name")
        self._style_input(self.signup_name)
        layout.addWidget(self.signup_name)

        layout.addWidget(self._field_label("Patient ID"))

        self.signup_id = QLineEdit()
        self.signup_id.setPlaceholderText("Choose a unique Patient ID")
        self._style_input(self.signup_id)
        layout.addWidget(self.signup_id)

        layout.addWidget(self._field_label("Password"))

        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText(
            "Create a password (minimum 8 characters)"
        )
        self.signup_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._style_input(self.signup_password)
        layout.addWidget(self.signup_password)

        layout.addWidget(self._field_label("Confirm Password"))

        self.signup_confirm = QLineEdit()
        self.signup_confirm.setPlaceholderText("Re-enter your password")
        self.signup_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self._style_input(self.signup_confirm)
        self.signup_confirm.returnPressed.connect(self._signup)
        layout.addWidget(self.signup_confirm)

        self.signup_error = self._error_label()
        layout.addWidget(self.signup_error)

        self.signup_button = QPushButton("Create Account")
        self.signup_button.setFixedHeight(44)
        self.signup_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.signup_button.setStyleSheet(self._primary_button_style())
        self.signup_button.clicked.connect(self._signup)
        layout.addWidget(self.signup_button)

        layout.addStretch()
        self.pages.addWidget(page)

    # ---------------------------------------------------------
    # Shared styles
    # ---------------------------------------------------------

    @staticmethod
    def _field_label(text):
        label = QLabel(text)
        label.setStyleSheet(
            "color: #4C397A; font-size: 11px; font-weight: bold;"
        )
        return label

    @staticmethod
    def _error_label():
        label = QLabel("")
        label.setWordWrap(True)
        label.setMinimumHeight(20)
        label.setStyleSheet("color: #D63C55; font-size: 10px;")
        return label

    @staticmethod
    def _style_input(field):
        field.setFixedHeight(40)
        field.setMaxLength(128)
        field.setStyleSheet("""
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
        """)

    @staticmethod
    def _primary_button_style():
        return """
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7E5BE8, stop:1 #A878E0
                );
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 13px;
                font-weight: bold;
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
        """

    @staticmethod
    def _secondary_button_style():
        return """
            QPushButton {
                background-color: #F1ECFC;
                color: #6546C9;
                border: 1px solid #D6CCEE;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #E6DCFA;
            }
        """

    def _set_mode(self, mode):
        is_signup = mode == "signup"
        self.pages.setCurrentIndex(1 if is_signup else 0)

        self.signin_tab.setStyleSheet(
            self._secondary_button_style()
            if is_signup else self._primary_button_style()
        )
        self.signup_tab.setStyleSheet(
            self._primary_button_style()
            if is_signup else self._secondary_button_style()
        )

        self.signin_error.clear()
        self.signup_error.clear()

    # ---------------------------------------------------------
    # Actions
    # ---------------------------------------------------------

    def _login_demo(self):
        """Open the predefined demo patient."""
        self.signin_error.clear()
        self.login_requested.emit("PATIENT_01", "Alex Mercer")

    def _signin(self):
        self.signin_error.clear()

        patient_id = self.signin_id.text().strip()
        password = self.signin_password.text()

        if not patient_id:
            self.signin_error.setText("Please enter your Patient ID.")
            self.signin_id.setFocus()
            return

        if not password:
            self.signin_error.setText("Please enter your password.")
            self.signin_password.setFocus()
            return

        try:
            user = db_login(patient_id, password)

            user_id = user.get("user_id") or user.get("id")
            name = user.get("name")

            if not user_id or not name:
                self.signin_error.setText(
                    "The saved profile is missing required information."
                )
                return

            self.login_requested.emit(str(user_id), str(name))

        except AuthError as exc:
            self.signin_error.setText(str(exc))

        except Exception:
            self.signin_error.setText(
                "Unable to sign in. Please check your details and try again."
            )

    def _signup(self):
        self.signup_error.clear()

        name = self.signup_name.text().strip()
        patient_id = self.signup_id.text().strip()
        password = self.signup_password.text()
        confirm = self.signup_confirm.text()

        if not name:
            self.signup_error.setText("Please enter your full name.")
            self.signup_name.setFocus()
            return

        if not patient_id:
            self.signup_error.setText("Please choose a Patient ID.")
            self.signup_id.setFocus()
            return

        if len(password) < 8:
            self.signup_error.setText(
                "Your password must contain at least 8 characters."
            )
            self.signup_password.setFocus()
            return

        if password != confirm:
            self.signup_error.setText("The passwords do not match.")
            self.signup_confirm.setFocus()
            return

        try:
            user = db_register(patient_id, name, password)

            user_id = user.get("user_id") or user.get("id")
            user_name = user.get("name")

            if not user_id or not user_name:
                self.signup_error.setText(
                    "The profile was created, but its details were incomplete."
                )
                return

            self.login_requested.emit(str(user_id), str(user_name))

        except AuthError as exc:
            self.signup_error.setText(str(exc))

        except Exception:
            self.signup_error.setText(
                "Unable to create the account. Please try again."
            )
