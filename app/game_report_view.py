
"""
Game Report View
----------------
Rehabilitation report displaying kinematics and biomechanics
alongside game session performance.

Metrics are loaded from local_data.py and the Unity session
JSON files imported by the application.
"""

import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from stat_card import make_stat_card
from local_data import (
    get_latest_session_summary,
    get_game_display_name,
    import_unity_session,
)


REPORT_SECTIONS = [
    {
        "title": "🩺 Biomechanics & Clinical Kinematics",
        "cards": [
            ("rom", "°", 1, "Active ROM", "#7E5BE8"),
            ("accuracy", "%", 1, "Trajectory Accuracy", "#38A169"),
            ("smoothness", "", 3, "Movement Smoothness", "#2B6CB0"),
            ("trajectory_deviation", "", 3, "Path Deviation", "#D69E2E"),
            ("avg_speed", " m/s", 2, "Average Speed", "#7E5BE8"),
            ("compensation_ratio", "", 3, "Compensatory Ratio", "#E53E3E"),
        ],
    },
    {
        "title": "🎮 Session Performance",
        "cards": [
            ("score", " pts", 0, "Session Score", "#7E5BE8"),
            ("targets_collected", "", 0, "Targets Collected", "#38A169"),
            ("best_streak", "", 0, "Best Target Streak", "#2B6CB0"),
            ("session_duration", " s", 1, "Session Duration", "#7E5BE8"),
        ],
    },
]


def _fmt(value, suffix="", decimals=1):
    """Format a metric safely, displaying a dash when unavailable."""
    if value is None or value == "":
        return "—"

    try:
        number = float(value)
    except (TypeError, ValueError):
        return "—"

    if not (float("-inf") < number < float("inf")):
        return "—"

    return f"{number:.{decimals}f}{suffix}"


def _numeric_value(summary, key):
    """Return a finite numeric value, or None if unavailable."""
    value = summary.get(key)

    if value is None or value == "":
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if not (float("-inf") < number < float("inf")):
        return None

    return number


class GameReportView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._current_user_id = "PATIENT_01"
        self._current_game_id = "reach_and_collect"
        self._card_labels = {}

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(12)

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        header_row = QHBoxLayout()
        title_column = QVBoxLayout()
        title_column.setSpacing(2)

        title = QLabel("Rehabilitation Clinical Report")

        title_font = QFont("Segoe UI", 18)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(
            "color: #2F2154; background: transparent;"
        )

        title_column.addWidget(title)

        self._subtitle = QLabel(
            "Session metrics from the RehabQuest movement analysis engine"
        )
        self._subtitle.setWordWrap(True)
        self._subtitle.setStyleSheet(
            "color: #7A6C9B; font-size: 11px; "
            "background: transparent;"
        )
        title_column.addWidget(self._subtitle)

        header_row.addLayout(title_column)
        header_row.addStretch()

        self._game_badge = QLabel("Reach & Collect")
        self._game_badge.setStyleSheet("""
            background-color: rgba(126, 91, 232, 25);
            color: #7E5BE8;
            font-weight: bold;
            font-size: 11px;
            padding: 6px 14px;
            border-radius: 12px;
            border: 1px solid rgba(126, 91, 232, 40);
        """)
        header_row.addWidget(self._game_badge)

        self.sync_btn = QPushButton("↻ Sync Latest Session")
        self.sync_btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.sync_btn.setFixedHeight(34)
        self.sync_btn.setStyleSheet("""
            QPushButton {
                background: #7E5BE8;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 11px;
                padding: 0 14px;
                border-radius: 10px;
                border: none;
            }

            QPushButton:hover {
                background: #6A48D7;
            }

            QPushButton:disabled {
                background: #C5B8E6;
            }
        """)
        self.sync_btn.clicked.connect(self._sync_and_reload)
        header_row.addWidget(self.sync_btn)

        main_layout.addLayout(header_row)

        # -------------------------------------------------
        # Scrollable report
        # -------------------------------------------------

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet(
            "background: transparent;"
        )

        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(0, 4, 10, 10)
        content_layout.setSpacing(16)

        # -------------------------------------------------
        # Metric sections
        # -------------------------------------------------

        for section in REPORT_SECTIONS:
            section_title = QLabel(section["title"])

            section_font = QFont("Segoe UI", 12)
            section_font.setWeight(QFont.Weight.Bold)
            section_title.setFont(section_font)
            section_title.setStyleSheet(
                "color: #4C397A; background: transparent;"
            )

            content_layout.addWidget(section_title)

            grid = QGridLayout()
            grid.setSpacing(12)

            for index, (
                key,
                suffix,
                decimals,
                label,
                accent,
            ) in enumerate(section["cards"]):

                card, value_label = make_stat_card(
                    "—",
                    label,
                    accent=accent,
                )

                self._card_labels[key] = (
                    value_label,
                    suffix,
                    decimals,
                )

                row, column = divmod(index, 3)
                grid.addWidget(card, row, column)

            content_layout.addLayout(grid)

        # -------------------------------------------------
        # Assessment and summary
        # -------------------------------------------------

        note_card = QFrame()
        note_card.setObjectName("noteCard")
        note_card.setStyleSheet("""
            QFrame#noteCard {
                background-color: rgba(255, 255, 255, 220);
                border-radius: 16px;
                border-left: 4px solid #7E5BE8;
            }

            QLabel {
                border: none;
                background: transparent;
            }
        """)

        note_layout = QVBoxLayout(note_card)
        note_layout.setContentsMargins(16, 12, 16, 12)
        note_layout.setSpacing(8)

        note_heading = QLabel("Session Assessment & Summary")
        note_heading.setStyleSheet("""
            color: #2F2154;
            font-weight: bold;
            font-size: 12px;
            background: transparent;
        """)
        note_layout.addWidget(note_heading)

        self._assessment_lbl = QLabel(
            "No recorded session is available. Complete an exercise "
            "and sync the session to view its recorded metrics."
        )
        self._assessment_lbl.setWordWrap(True)
        self._assessment_lbl.setStyleSheet("""
            color: #6C5D8C;
            font-size: 11px;
            background: transparent;
        """)
        note_layout.addWidget(self._assessment_lbl)

        self._data_note = QLabel(
            "Note: Metrics depend on the values recorded by the "
            "movement-analysis pipeline. They should not be treated "
            "as a clinical diagnosis."
        )
        self._data_note.setWordWrap(True)
        self._data_note.setStyleSheet("""
            color: #8A7CA3;
            font-size: 10px;
            background: transparent;
        """)
        note_layout.addWidget(self._data_note)

        content_layout.addWidget(note_card)
        content_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

    # -----------------------------------------------------
    # Load report
    # -----------------------------------------------------

    def load(self, user_id, game_id="reach_and_collect"):
        """Load the latest recorded session for a user and game."""
        self._current_user_id = user_id
        self._current_game_id = game_id

        self._game_badge.setText(
            get_game_display_name(game_id)
        )

        summary = get_latest_session_summary(
            user_id,
            game_id,
        )

        if not summary:
            self._clear_metrics()
            self._assessment_lbl.setText(
                "No recorded sessions were found for this exercise. "
                "Complete a session and use Sync Latest Session."
            )
            return

        for key, (
            value_label,
            suffix,
            decimals,
        ) in self._card_labels.items():

            value = summary.get(key)
            value_label.setText(
                _fmt(value, suffix, decimals)
            )

        self._update_assessment(summary)

    def _clear_metrics(self):
        """Reset all metric cards when there is no session."""
        for value_label, _, _ in self._card_labels.values():
            value_label.setText("—")

    def _update_assessment(self, summary):
        """Create a factual summary from metrics that are available."""
        parts = []

        rom = _numeric_value(summary, "rom")
        accuracy = _numeric_value(summary, "accuracy")
        smoothness = _numeric_value(summary, "smoothness")
        duration = _numeric_value(summary, "session_duration")
        targets = _numeric_value(summary, "targets_collected")

        if rom is not None:
            parts.append(f"Recorded active ROM: {rom:.1f}°")

        if accuracy is not None:
            parts.append(
                f"recorded trajectory accuracy: {accuracy:.1f}%"
            )

        if smoothness is not None:
            parts.append(
                f"movement smoothness metric: {smoothness:.3f}"
            )

        if duration is not None:
            parts.append(
                f"session duration: {duration:.1f} seconds"
            )

        if targets is not None:
            parts.append(
                f"targets collected: {int(targets)}"
            )

        compensation_status = summary.get(
            "compensation_status"
        )

        if compensation_status:
            parts.append(
                f"movement-analysis status: {compensation_status}"
            )

        if parts:
            self._assessment_lbl.setText(
                "Recorded session results: "
                + "; ".join(parts)
                + "."
            )
        else:
            self._assessment_lbl.setText(
                "A session was found, but it does not contain "
                "enough recorded metrics to generate a summary."
            )

    # -----------------------------------------------------
    # Unity session sync
    # -----------------------------------------------------

    def _get_session_directories(self):
        """Return likely locations for Unity session exports."""
        directories = []

        user_profile = os.environ.get("USERPROFILE")

        if user_profile:
            directories.append(
                Path(user_profile)
                / "AppData"
                / "LocalLow"
                / "DefaultCompany"
                / "RehabQuest-Unity"
                / "RehabQuestSessions"
            )

        project_root = Path(__file__).resolve().parent.parent

        directories.extend([
            project_root / "RehabQuestSessions",
            project_root
            / "RehabQuest-Unity"
            / "RehabQuestSessions",
        ])

        # Preserve order while removing duplicates.
        return list(dict.fromkeys(directories))

    def _sync_and_reload(self):
        """Import the newest Unity export, then refresh the report."""
        self.sync_btn.setEnabled(False)
        self.sync_btn.setText("Syncing...")

        try:
            candidates = []

            for directory in self._get_session_directories():
                if directory.exists():
                    candidates.extend(
                        directory.glob(
                            "reach_and_collect_session_*.json"
                        )
                    )

            if candidates:
                latest_file = max(
                    candidates,
                    key=lambda file: file.stat().st_mtime,
                )

                import_unity_session(
                    str(latest_file),
                    self._current_user_id,
                )

            self.load(
                self._current_user_id,
                self._current_game_id,
            )

        except Exception as exc:
            self._assessment_lbl.setText(
                "Could not sync the Unity session. "
                f"Details: {exc}"
            )

        finally:
            self.sync_btn.setEnabled(True)
            self.sync_btn.setText("↻ Sync Latest Session")
