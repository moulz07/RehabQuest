
"""
Progress View
-------------
RehabQuest patient recovery tracking.

Displays rehabilitation progress across consecutive sessions:
- Active Range of Motion (ROM)
- Movement trajectory accuracy
- Movement smoothness

Session history is loaded from local_data.py.
Only recorded metric values are plotted.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
)
from PyQt6.QtGui import QFont

from progress_chart import ProgressChart
from stat_card import make_stat_card
from local_data import (
    get_current_streak,
    get_best_streak,
    get_total_sessions,
    get_session_history,
)


# Metric keys must match the fields returned by get_session_history().
CHART_CONFIGS = [
    {
        "title": "Active Range of Motion (ROM)",
        "y_max": None,
        "y_suffix": "°",
        "series": [
            {
                "key": "rom",
                "label": "Active ROM",
                "color": "#7E5BE8",
            },
            {
                "key": "flexion_rom",
                "label": "Flexion",
                "color": "#A878E0",
            },
        ],
    },
    {
        "title": "Movement Trajectory Accuracy",
        "y_max": 100,
        "y_suffix": "%",
        "series": [
            {
                "key": "accuracy",
                "label": "Accuracy",
                "color": "#38A169",
            },
        ],
    },
    {
        "title": "Movement Smoothness",
        "y_max": None,
        "y_suffix": "",
        "series": [
            {
                "key": "smoothness",
                "label": "Smoothness",
                "color": "#3182CE",
            },
        ],
    },
]


class ProgressView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._current_user_id = "PATIENT_01"
        self._charts = []

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(12)

        # --------------------------------------------------
        # Header
        # --------------------------------------------------
        header_row = QHBoxLayout()
        title_column = QVBoxLayout()
        title_column.setSpacing(2)

        title = QLabel("Recovery Progress & Trends")
        title_font = QFont("Segoe UI", 18)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(
            "color: #2F2154; background: transparent;"
        )
        title_column.addWidget(title)

        subtitle = QLabel(
            "Track mobility, movement accuracy, and smoothness "
            "across rehabilitation sessions."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            "color: #7A6C9B; font-size: 11px; "
            "background: transparent;"
        )
        title_column.addWidget(subtitle)

        header_row.addLayout(title_column)
        header_row.addStretch()

        main_layout.addLayout(header_row)

        # --------------------------------------------------
        # Scrollable content
        # --------------------------------------------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")

        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(0, 4, 10, 10)
        content_layout.setSpacing(16)

        # --------------------------------------------------
        # Summary statistic cards
        # --------------------------------------------------
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        card1, self.lbl_current_streak = make_stat_card(
            "0",
            "Current Streak",
            "#7E5BE8",
        )

        card2, self.lbl_best_streak = make_stat_card(
            "0",
            "Best Streak",
            "#2B6CB0",
        )

        card3, self.lbl_total_sessions = make_stat_card(
            "0",
            "Total Sessions",
            "#38A169",
        )

        stats_row.addWidget(card1)
        stats_row.addWidget(card2)
        stats_row.addWidget(card3)

        content_layout.addLayout(stats_row)

        # --------------------------------------------------
        # Rehabilitation charts
        # --------------------------------------------------
        for config in CHART_CONFIGS:
            chart_panel = QFrame()
            chart_panel.setObjectName("chartPanel")

            chart_panel.setStyleSheet("""
                QFrame#chartPanel {
                    background-color: rgba(255, 255, 255, 225);
                    border-radius: 18px;
                    border: 1px solid rgba(133, 103, 232, 25);
                }

                QLabel {
                    border: none;
                    background: transparent;
                }
            """)

            chart_layout = QVBoxLayout(chart_panel)
            chart_layout.setContentsMargins(18, 14, 18, 14)
            chart_layout.setSpacing(8)

            # Chart title and legend
            chart_header = QHBoxLayout()
            chart_header.setSpacing(10)

            chart_title = QLabel(config["title"])
            chart_title.setWordWrap(True)
            chart_title.setStyleSheet(
                "color: #4C397A; font-weight: bold; "
                "font-size: 13px; background: transparent;"
            )

            chart_header.addWidget(chart_title)
            chart_header.addStretch()

            for metric in config["series"]:
                legend_label = QLabel(
                    f"● {metric['label']}"
                )
                legend_label.setStyleSheet(
                    f"color: {metric['color']}; "
                    "font-size: 10px; font-weight: bold; "
                    "background: transparent;"
                )
                chart_header.addWidget(legend_label)

            chart_layout.addLayout(chart_header)

            # Chart widget
            chart = ProgressChart()
            chart.setMinimumHeight(200)

            chart_layout.addWidget(chart)

            self._charts.append((chart, config))
            content_layout.addWidget(chart_panel)

        content_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

    def refresh_for_user(self, user_id):
        """
        Refresh summary cards and rehabilitation charts
        for the selected patient.
        """
        self._current_user_id = user_id

        # Summary statistics
        self.lbl_current_streak.setText(
            str(get_current_streak(user_id))
        )

        self.lbl_best_streak.setText(
            str(get_best_streak(user_id))
        )

        self.lbl_total_sessions.setText(
            str(get_total_sessions(user_id))
        )

        # Retrieve real session history
        history = get_session_history(
            user_id,
            "reach_and_collect",
        ) or []

        # Feed the same session history into each chart.
        for chart, config in self._charts:
            chart.load(
                history=history,
                series=config["series"],
                y_max=config["y_max"],
                y_suffix=config["y_suffix"],
            )
