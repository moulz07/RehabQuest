"""
RehabQuest - Main Desktop Application
-------------------------------------
Desktop application shell combining login and the clinical dashboard.
Launch using:
    python app/main.py
"""

import sys
import os
from pathlib import Path

# Ensure app directory is on path
APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QStackedWidget, QPushButton, QHBoxLayout, QVBoxLayout,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor

from login_page import LoginPage
from dashboard_page import DashboardPage

WINDOW_W = 960
WINDOW_H = 620


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RehabQuest")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(WINDOW_W, WINDOW_H)
        self._drag_pos = None

        self._build_ui()
        self._center_on_screen()

    def _center_on_screen(self):
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            x = (geo.width() - WINDOW_W) // 2
            y = (geo.height() - WINDOW_H) // 2
            self.move(x, y)

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)

        # Container frame with shadow & rounded look
        self.container = QWidget(self)
        self.container.setObjectName("mainContainer")
        self.container.setStyleSheet("""
            QWidget#mainContainer {
                background-color: #F8F5FC;
                border-radius: 20px;
                border: 1px solid rgba(133, 103, 232, 40);
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(40, 20, 80, 70))
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Top Bar with Window Controls
        top_bar = QWidget(self.container)
        top_bar.setFixedHeight(34)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(12, 6, 12, 0)
        top_layout.addStretch()

        min_btn = QPushButton("—", top_bar)
        min_btn.setFixedSize(26, 22)
        min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        min_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #7E5BE8;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: rgba(126, 91, 232, 30); }
        """)
        min_btn.clicked.connect(self.showMinimized)
        top_layout.addWidget(min_btn)

        close_btn = QPushButton("\u2715", top_bar)
        close_btn.setFixedSize(26, 22)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #7E5BE8;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #E53E3E; color: white; }
        """)
        close_btn.clicked.connect(self.close)
        top_layout.addWidget(close_btn)

        container_layout.addWidget(top_bar)

        # Pages Stack
        self.stack = QStackedWidget(self.container)
        self.login_page = LoginPage(self.stack)
        self.dashboard_page = DashboardPage(self.stack)

        self.login_page.login_requested.connect(self._on_login_success)

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.dashboard_page)
        self.stack.setCurrentWidget(self.login_page)

        container_layout.addWidget(self.stack, 1)
        root_layout.addWidget(self.container)

    def _on_login_success(self, user_id, name):
        self.dashboard_page.set_user(user_id, name)
        self.stack.setCurrentWidget(self.dashboard_page)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
