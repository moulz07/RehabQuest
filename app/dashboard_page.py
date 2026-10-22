
"""
Dashboard Page for RehabQuest
-----------------------------
Main container combining the soft bloom background, persistent sidebar,
and navigation between Home, Games, Instructions, Report, and Progress.
"""

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QStackedWidget,
    QMessageBox,
)

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

        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(18)

        # -------------------------------------------------
        # Sidebar
        # -------------------------------------------------

        self.sidebar = Sidebar(self)
        self.sidebar.nav_changed.connect(
            self._on_nav_changed
        )
        layout.addWidget(self.sidebar)

        # -------------------------------------------------
        # Page stack
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

        layout.addWidget(self.content_stack, 1)

        # -------------------------------------------------
        # Home navigation
        # -------------------------------------------------

        self.home_view.play_requested.connect(
            lambda: self._switch_to("games")
        )

        # The HomeView emits category_requested when a specific
        # category is selected. That handler also opens Games,
        # so games_requested is not connected separately here.
        self.home_view.category_requested.connect(
            self._on_home_category_requested
        )

        # This signal is used for general Explore Games actions
        # that don't select a particular category.
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
        # Game launcher
        # -------------------------------------------------

        self.launcher = GameLauncher(self)

        self.launcher.game_started.connect(
            self._on_game_started
        )

        self.launcher.game_finished.connect(
            self._on_game_finished
        )

    # -----------------------------------------------------
    # User profile
    # -----------------------------------------------------

    def set_user(self, user_id, name):
        """Set the active user and refresh user-specific pages."""
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

        self.progress_view.refresh_for_user(
            user_id
        )

        self.report_view.load(
            user_id,
            "reach_and_collect",
        )

    # -----------------------------------------------------
    # Navigation
    # -----------------------------------------------------

    def _on_nav_changed(self, key):
        self._switch_to(key)

    def _switch_to(self, key):
        """Switch to a page and refresh data where necessary."""
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

    def _open_games_from_home(self):
        self._switch_to("games")

    def _on_home_category_requested(self, category_id):
        """Open Games and expand the selected category."""
        self.games_view.open_category(category_id)
        self._switch_to("games")

    # -----------------------------------------------------
    # Exercise launch
    # -----------------------------------------------------

    def _show_instructions(self, game_id):
        self.instructions_page.load(game_id)
        self._switch_to("instructions")

    def _start_game_session(self, game_id):
        """Request a game launch for the current user."""
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

        # GameLauncher.launch() currently reports failures through
        # console output rather than a return value or error signal.
        # Therefore, do not show a success dialog here. The
        # game_started signal displays it only after Unity launches.

    def _on_game_started(self, game_id):
        """Show confirmation after Unity has actually launched."""
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

    # -----------------------------------------------------
    # Session completion
    # -----------------------------------------------------

    def _on_game_finished(self, game_id):
        """Refresh user data and open the latest report."""
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
