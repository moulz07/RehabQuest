
"""
Dashboard Page for RehabQuest
-----------------------------
Main container combining the soft bloom background, persistent sidebar,
and navigation between Home, Games, Instructions, Report, and Progress.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QStackedWidget,
    QLabel,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal

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

    session_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_user_id = "PATIENT_01"
        self.current_user_name = "Alex Mercer"

        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(18)

        # Left sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.nav_changed.connect(self._on_nav_changed)
        layout.addWidget(self.sidebar)

        # Content stack
        self.content_stack = QStackedWidget(self)
        self.content_stack.setStyleSheet("background: transparent;")

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

        layout.addWidget(self.content_stack, 1)

        # Home navigation
        self.home_view.play_requested.connect(
            lambda: self._switch_to("games")
        )

        # Explore games: open Games and expand the requested category.
        self.home_view.games_requested.connect(
            self._open_games_from_home
        )
        self.home_view.category_requested.connect(
            self._on_home_category_requested
        )

        # Game selection and instructions
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

        # Game launcher
        self.launcher = GameLauncher(self)
        self.launcher.game_started.connect(self._on_game_started)
        self.launcher.game_finished.connect(self._on_game_finished)

    def set_user(self, user_id, name):
        self.current_user_id = user_id
        self.current_user_name = name

        self.sidebar.set_user_name(name)
        self.sidebar.set_streak(get_current_streak(user_id))

        self.home_view.refresh_for_user(user_id, name)
        self.progress_view.refresh_for_user(user_id)
        self.report_view.load(user_id, "reach_and_collect")

    def _on_nav_changed(self, key):
        self._switch_to(key)

    def _switch_to(self, key):
        mapping = {
            "home": self.home_view,
            "games": self.games_view,
            "body_parts": self.body_parts_view,
            "instructions": self.instructions_page,
            "report": self.report_view,
            "progress": self.progress_view,
        }

        target = mapping.get(key)

        if target:
            if key == "report":
                self.report_view.load(
                    self.current_user_id,
                    "reach_and_collect",
                )

            elif key == "progress":
                self.progress_view.refresh_for_user(
                    self.current_user_id
                )

            self.content_stack.setCurrentWidget(target)
            self.sidebar.set_active(key)

    def _open_games_from_home(self):
        self._switch_to("games")

    def _on_home_category_requested(self, category_id):
        # Open the Games page and expand the requested category.
        self.games_view.open_category(category_id)
        self._switch_to("games")

    def _show_instructions(self, game_id):
        self.instructions_page.load(game_id)
        self.content_stack.setCurrentWidget(self.instructions_page)

    def _start_game_session(self, game_id):
        self.launcher.launch(
            game_id,
            self.current_user_id,
        )

    def _on_game_started(self, game_id):
        msg = QMessageBox(self)
        msg.setWindowTitle("RehabQuest Tracking Active")
        msg.setText(
            "<b>✅ RehabQuest Session Started!</b><br><br>"
            "1. MediaPipe tracking has been started.<br>"
            "2. Reach &amp; Collect is launching automatically.<br><br>"
            "<i>Complete the exercise in the game window. "
            "Your report will open when the game closes.</i>"
        )

        msg.setStyleSheet("""
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

        msg.exec()

    def _on_game_finished(self, game_id):
        # Open the Report tab when a session completes.
        self._switch_to("report")
