
"""
Dashboard Page for RehabQuest
-----------------------------
Dashboard with a collapsible animated sidebar and navigation
between Home, Games, Instructions, Report, and Progress.
"""

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
    QPushButton,
    QFrame,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

from bloom_background import BloomPage
from sidebar import Sidebar
from home_view import HomeView
from games_view import GamesView
from instructions_page import InstructionsPage
from game_report_view import GameReportView
from progress_view import ProgressView
from body_parts_view import BodyPartsView
from local_data import get_current_streak
from game_launcher import GameLauncher


class DashboardPage(BloomPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_user_id = "PATIENT_01"
        self.current_user_name = "Alex Mercer"
        self._active_game_id = None

        self._sidebar_open = False
        self._sidebar_width = 200

        self._build_ui()

    def _build_ui(self):
        # Main vertical layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(18, 12, 18, 18)
        root_layout.setSpacing(8)

        # -------------------------------------------------
        # Top bar with hamburger menu
        # -------------------------------------------------
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        self.menu_button = QPushButton("☰")
        self.menu_button.setFixedSize(44, 40)
        self.menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_button.setToolTip("Open navigation menu")
        self.menu_button.setStyleSheet("""
            QPushButton {
                background-color: #7E5BE8;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 23px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #6945D1;
            }
        """)
        self.menu_button.clicked.connect(self._toggle_sidebar)
        top_bar.addWidget(self.menu_button)

        self.top_title = QPushButton("REHABQUEST")
        self.top_title.setCursor(Qt.CursorShape.PointingHandCursor)
        self.top_title.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #38245F;
                border: none;
                font-size: 15px;
                font-weight: bold;
                text-align: left;
            }

            QPushButton:hover {
                color: #7E5BE8;
            }
        """)
        self.top_title.clicked.connect(
            lambda: self._switch_to("home")
        )
        top_bar.addWidget(self.top_title)
        top_bar.addStretch()

        root_layout.addLayout(top_bar)

        # -------------------------------------------------
        # Main horizontal layout
        # -------------------------------------------------
        self.main_row = QHBoxLayout()
        self.main_row.setContentsMargins(0, 0, 0, 0)
        self.main_row.setSpacing(12)

        # Sidebar container
        self.sidebar_frame = QFrame(self)
        self.sidebar_frame.setObjectName("sidebarFrame")
        self.sidebar_frame.setMinimumWidth(0)
        self.sidebar_frame.setMaximumWidth(self._sidebar_width)
        self.sidebar_frame.setStyleSheet("""
            QFrame#sidebarFrame {
                background: transparent;
                border: none;
            }
        """)

        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        self.sidebar = Sidebar(self.sidebar_frame)
        self.sidebar.nav_changed.connect(self._on_nav_changed)
        sidebar_layout.addWidget(self.sidebar)

        self.main_row.addWidget(self.sidebar_frame)

        # Start with sidebar hidden
        self.sidebar_frame.hide()

        # -------------------------------------------------
        # Main page stack
        # -------------------------------------------------
        self.content_stack = QStackedWidget(self)
        self.content_stack.setStyleSheet(
            "background: transparent;"
        )

        self.home_view = HomeView(self)
        self.games_view = GamesView(self)
        self.body_parts_view = BodyPartsView(self)
        self.instructions_page = InstructionsPage(self)
        self.report_view = GameReportView(self)
        self.progress_view = ProgressView(self)

        self.content_stack.addWidget(self.home_view)
        self.content_stack.addWidget(self.games_view)
        self.content_stack.addWidget(self.body_parts_view)
        self.content_stack.addWidget(self.instructions_page)
        self.content_stack.addWidget(self.report_view)
        self.content_stack.addWidget(self.progress_view)

        self.main_row.addWidget(self.content_stack, 1)
        root_layout.addLayout(self.main_row, 1)

        # -------------------------------------------------
        # Sidebar width animation
        # -------------------------------------------------
        self.sidebar_animation = QPropertyAnimation(
            self.sidebar_frame,
            b"maximumWidth",
            self,
        )
        self.sidebar_animation.setDuration(220)
        self.sidebar_animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )
        self.sidebar_animation.finished.connect(
            self._finish_sidebar_animation
        )

        # -------------------------------------------------
        # Home navigation
        # -------------------------------------------------
        self.home_view.play_requested.connect(
            lambda: self._switch_to("games")
        )

        self.home_view.category_requested.connect(
            self._on_home_category_requested
        )

        self.home_view.games_requested.connect(
            self._open_games_from_home
        )

        # -------------------------------------------------
        # Exercise selection and instructions
        # -------------------------------------------------
        self.games_view.game_selected.connect(
            self._show_instructions
        )

        self.body_parts_view.exercise_selected.connect(
            self._show_instructions
        )

        self.instructions_page.back_requested.connect(
            lambda: self._switch_to("games")
        )

        self.instructions_page.play_confirmed.connect(
            self._start_game_session
        )

        # -------------------------------------------------
        # Unity game launcher
        # -------------------------------------------------
        self.launcher = GameLauncher(self)

        self.launcher.game_started.connect(
            self._on_game_started
        )

        self.launcher.game_finished.connect(
            self._on_game_finished
        )

    # =====================================================
    # SIDEBAR CONTROLS
    # =====================================================

    def _toggle_sidebar(self):
        if self._sidebar_open:
            self._close_sidebar()
        else:
            self._open_sidebar()

    def _open_sidebar(self):
        if self._sidebar_open:
            return

        self._sidebar_open = True

        # Reveal the sidebar before animating its width.
        self.sidebar_frame.show()
        self.sidebar_frame.setMinimumWidth(0)
        self.sidebar_frame.setMaximumWidth(0)

        self.sidebar_animation.stop()
        self.sidebar_animation.setStartValue(0)
        self.sidebar_animation.setEndValue(
            self._sidebar_width
        )
        self.sidebar_animation.start()

        self.menu_button.setText("✕")
        self.menu_button.setToolTip("Close navigation menu")

    def _close_sidebar(self):
        if not self._sidebar_open:
            return

        self._sidebar_open = False

        self.sidebar_animation.stop()
        self.sidebar_frame.setMinimumWidth(0)

        self.sidebar_animation.setStartValue(
            self.sidebar_frame.width()
        )
        self.sidebar_animation.setEndValue(0)
        self.sidebar_animation.start()

        self.menu_button.setText("☰")
        self.menu_button.setToolTip("Open navigation menu")

    def _finish_sidebar_animation(self):
        if self._sidebar_open:
            self.sidebar_frame.setMinimumWidth(
                self._sidebar_width
            )
            self.sidebar_frame.setMaximumWidth(
                self._sidebar_width
            )
        else:
            self.sidebar_frame.hide()
            self.sidebar_frame.setMinimumWidth(0)
            self.sidebar_frame.setMaximumWidth(
                self._sidebar_width
            )

    # =====================================================
    # USER PROFILE
    # =====================================================

    def set_user(self, user_id, name):
        """Set the current patient and refresh dashboard data."""
        self.current_user_id = user_id
        self.current_user_name = name

        self.sidebar.set_user_name(name)
        self.sidebar.set_streak(
            get_current_streak(user_id)
        )

        self.home_view.refresh_for_user(
            user_id,
            name,
        )

        self.progress_view.refresh_for_user(user_id)

        self.report_view.load(
            user_id,
            "reach_and_collect",
        )

    # =====================================================
    # NAVIGATION
    # =====================================================

    def _on_nav_changed(self, key):
        self._switch_to(key)

    def _switch_to(self, key):
        """Switch page, refresh data, and close the sidebar."""
        pages = {
            "home": self.home_view,
            "games": self.games_view,
            "body_parts": self.body_parts_view,
            "instructions": self.instructions_page,
            "report": self.report_view,
            "progress": self.progress_view,
        }

        target = pages.get(key)

        if target is None:
            return

        if key == "home":
            self.home_view.refresh_for_user(
                self.current_user_id,
                self.current_user_name,
            )

        elif key == "report":
            game_id = (
                self._active_game_id
                or "reach_and_collect"
            )
            self.report_view.load(
                self.current_user_id,
                game_id,
            )

        elif key == "progress":
            self.progress_view.refresh_for_user(
                self.current_user_id
            )

        self.content_stack.setCurrentWidget(target)
        self.sidebar.set_active(key)

        # Close the menu after navigating.
        self._close_sidebar()

    def _open_games_from_home(self):
        self._switch_to("games")

    def _on_home_category_requested(self, category_id):
        self.games_view.open_category(category_id)
        self._switch_to("games")

    # =====================================================
    # EXERCISE LAUNCH
    # =====================================================

    def _show_instructions(self, game_id):
        self.instructions_page.load(game_id)
        self._switch_to("instructions")

    def _start_game_session(self, game_id):
        if self._active_game_id is not None:
            QMessageBox.information(
                self,
                "Session in Progress",
                "A rehabilitation session is already running.",
            )
            return

        self._active_game_id = game_id

        self.launcher.launch(
            game_id,
            self.current_user_id,
        )

    def _on_game_started(self, game_id):
        self._active_game_id = game_id

        message = QMessageBox(self)
        message.setWindowTitle(
            "RehabQuest Tracking Active"
        )
        message.setText(
            "<b>RehabQuest session started!</b><br><br>"
            "The tracking server is running and the game has launched."
            "<br><br>"
            "<i>Complete the exercise in the game window. "
            "Your report will refresh when the game closes.</i>"
        )

        message.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
            }

            QLabel {
                color: #2F2154;
                font-size: 12px;
            }

            QPushButton {
                background-color: #7E5BE8;
                color: white;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: bold;
            }
        """)

        message.exec()

    # =====================================================
    # SESSION COMPLETION
    # =====================================================

    def _on_game_finished(self, game_id):
        self._active_game_id = None

        self.home_view.refresh_for_user(
            self.current_user_id,
            self.current_user_name,
        )

        self.sidebar.set_streak(
            get_current_streak(self.current_user_id)
        )

        self.progress_view.refresh_for_user(
            self.current_user_id
        )

        self.report_view.load(
            self.current_user_id,
            game_id,
        )

        self._switch_to("report")
