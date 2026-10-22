
"""
Home View for RehabQuest
------------------------
Gaming-inspired dashboard with patient greeting, exercise categories,
performance metrics, weekly activity and progress overview.
"""

from datetime import date

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QPushButton,
    QScrollArea,
    QProgressBar,
)
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt6.QtGui import (
    QFont,
    QPainter,
    QLinearGradient,
    QRadialGradient,
    QColor,
    QPainterPath,
    QPen,
    QPolygonF,
)

from decorative_shapes import draw_star_field
from local_data import (
    get_current_streak,
    get_weekly_session_days,
    get_random_quote,
)
from weekly_activity import WeeklyActivityCard


BG = "#F6F4FC"
PURPLE = "#7957E8"
PURPLE_DARK = "#5D3CC8"
DARK = "#292044"
MUTED = "#817995"
BORDER = "#EAE5F4"

TEAL = "#36B8AD"
TEAL_LIGHT = "#E0F8F4"
ORANGE = "#FFAD5C"
ORANGE_LIGHT = "#FFF0DF"
PINK = "#F27EAE"
PINK_LIGHT = "#FFE7F0"
LAVENDER = "#EEE8FF"


def make_label(text, size=11, color=DARK, bold=False):
    label = QLabel(text)
    font = QFont("Segoe UI", size)
    font.setBold(bold)
    label.setFont(font)
    label.setStyleSheet(
        f"color: {color}; background: transparent; border: none;"
    )
    return label


def make_card(parent=None):
    card = QFrame(parent)
    card.setStyleSheet(f"""
        QFrame {{
            background: white;
            border: 1px solid {BORDER};
            border-radius: 17px;
        }}
        QLabel {{
            background: transparent;
            border: none;
        }}
    """)
    return card


# ---------------------------------------------------------
# Dashboard hero
# ---------------------------------------------------------

class DashboardHeroCard(QFrame):
    play_now_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user_name = "Patient"
        self._streak = 0
        self._build_ui()

    def paintEvent(self, event):
        width, height = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, width * 0.8, height)
        gradient.setColorAt(0, QColor("#6D4BDB"))
        gradient.setColorAt(0.55, QColor("#8869EC"))
        gradient.setColorAt(1, QColor("#B18AF3"))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(self.rect(), 22, 22)

        painter.save()
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, width, height), 22, 22)
        painter.setClipPath(path)

        glow = QRadialGradient(
            QPointF(width * 0.83, height * 0.25),
            max(100, width * 0.32),
        )
        glow.setColorAt(0, QColor(222, 206, 255, 105))
        glow.setColorAt(1, QColor(222, 206, 255, 0))

        painter.setBrush(glow)
        painter.drawEllipse(
            QPointF(width * 0.83, height * 0.25),
            width * 0.32,
            width * 0.32,
        )

        draw_star_field(
            painter, width, height * 0.8,
            count=16, seed=7,
            color=QColor(235, 225, 255),
        )
        painter.restore()
        painter.end()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(7)

        date_label = QLabel(
            date.today().strftime("%A, %B %d, %Y").upper()
        )
        date_label.setStyleSheet("""
            color: #EEE7FF;
            background: transparent;
            border: none;
            font-size: 9px;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        left.addWidget(date_label)

        self._greeting_label = QLabel(
            f"Welcome back,\n{self._user_name}!"
        )
        greeting_font = QFont("Segoe UI", 23)
        greeting_font.setWeight(QFont.Weight.Bold)
        self._greeting_label.setFont(greeting_font)
        self._greeting_label.setStyleSheet(
            "color: white; background: transparent; border: none;"
        )
        left.addWidget(self._greeting_label)

        description = QLabel(
            "Move, play and recover — one achievement at a time."
        )
        description.setWordWrap(True)
        description.setStyleSheet(
            "color: #F2EDFF; background: transparent; font-size: 11px;"
        )
        left.addWidget(description)
        left.addStretch()

        self._streak_text = QLabel(
            "✨ Start a new rehabilitation streak today!"
        )
        self._streak_text.setWordWrap(True)
        self._streak_text.setStyleSheet("""
            color: white;
            background: rgba(255,255,255,30);
            border: 1px solid rgba(255,255,255,60);
            border-radius: 9px;
            padding: 7px;
            font-size: 10px;
        """)
        left.addWidget(self._streak_text)

        play_button = QPushButton("▶  Start Daily Session")
        play_button.setCursor(Qt.CursorShape.PointingHandCursor)
        play_button.setMinimumHeight(42)
        play_button.setStyleSheet("""
            QPushButton {
                background: white;
                color: #5D3CC8;
                border: none;
                border-radius: 11px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background: #F2ECFF; }
        """)
        play_button.clicked.connect(self.play_now_clicked.emit)
        left.addWidget(play_button, 0, Qt.AlignmentFlag.AlignLeft)

        layout.addLayout(left, 1)

        art = QFrame()
        art.setMinimumWidth(105)
        art.setMaximumWidth(145)
        art.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,28);
                border: 1px solid rgba(255,255,255,65);
                border-radius: 22px;
            }
        """)
        art_layout = QVBoxLayout(art)

        game_icon = QLabel("🎮")
        game_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        game_icon.setStyleSheet(
            "font-size: 48px; background: transparent; border: none;"
        )
        art_layout.addWidget(game_icon)

        caption = QLabel("YOUR NEXT\nACHIEVEMENT")
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption.setStyleSheet("""
            color: white;
            background: transparent;
            border: none;
            font-size: 8px;
            font-weight: bold;
        """)
        art_layout.addWidget(caption)
        layout.addWidget(art, 0, Qt.AlignmentFlag.AlignVCenter)

    def set_user(self, name, streak):
        self._user_name = name
        self._streak = streak
        self._greeting_label.setText(f"Welcome back,\n{name}!")

        if streak > 0:
            self._streak_text.setText(
                f"🔥 {streak}-day streak! Keep your progress going."
            )
        else:
            self._streak_text.setText(
                "✨ Start a new rehabilitation streak today!"
            )


# ---------------------------------------------------------
# Exercise category card
# ---------------------------------------------------------

class ExerciseCategoryCard(QFrame):
    category_clicked = pyqtSignal(str)

    def __init__(
        self, category_id, icon, title, body_parts,
        description, accent, light, game_count=2, parent=None,
    ):
        super().__init__(parent)
        self.category_id = category_id

        self.setMinimumHeight(150)
        self.setStyleSheet(f"""
            QFrame {{
                background: {light};
                border: 1px solid {accent}55;
                border-radius: 17px;
            }}
            QLabel {{ background: transparent; border: none; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(5)

        top = QHBoxLayout()

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(38, 38)
        icon_label.setStyleSheet(f"""
            background: {accent};
            color: white;
            border-radius: 12px;
            font-size: 19px;
        """)
        top.addWidget(icon_label)
        top.addStretch()

        count_label = QLabel(f"{game_count} GAMES")
        count_label.setStyleSheet(f"""
            color: {accent};
            background: white;
            border-radius: 8px;
            padding: 5px 7px;
            font-size: 8px;
            font-weight: bold;
        """)
        top.addWidget(count_label)
        layout.addLayout(top)

        layout.addWidget(make_label(title, 13, DARK, True))
        layout.addWidget(make_label(body_parts, 9, accent, True))

        detail = make_label(description, 9, MUTED)
        detail.setWordWrap(True)
        layout.addWidget(detail)
        layout.addStretch()

        button = QPushButton("Explore games   →")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(f"""
            QPushButton {{
                background: white;
                color: {accent};
                border: 1px solid {accent}55;
                border-radius: 9px;
                padding: 7px;
                text-align: left;
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {light}; }}
        """)

        # Emit the selected category ID when clicked.
        button.clicked.connect(
            lambda checked=False, cid=category_id:
            self.category_clicked.emit(cid)
        )
        layout.addWidget(button)


# ---------------------------------------------------------
# Performance metric card
# ---------------------------------------------------------

class PerformanceMetricCard(QFrame):
    def __init__(self, icon, title, value, detail, accent, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid {BORDER};
                border-radius: 15px;
            }}
            QLabel {{ background: transparent; border: none; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 11, 12, 10)
        layout.setSpacing(5)

        top = QHBoxLayout()
        top.addWidget(make_label(icon, 16, accent, True))
        top.addStretch()
        top.addWidget(make_label(title, 8, MUTED, True))
        layout.addLayout(top)

        self.value_label = make_label(value, 21, DARK, True)
        layout.addWidget(self.value_label)
        layout.addWidget(make_label(detail, 8, MUTED))


# ---------------------------------------------------------
# Progress chart
# ---------------------------------------------------------

class ProgressTrendChart(QWidget):
    def __init__(self, values=None, parent=None):
        super().__init__(parent)
        self.values = values or [46, 62, 76, 87]
        self.setMinimumHeight(145)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(26, 12, -12, -26)

        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.setPen(QPen(QColor("#EEEAF5"), 1))
        painter.setFont(QFont("Segoe UI", 8))

        for value in (0, 25, 50, 75, 100):
            y = rect.bottom() - value / 100 * rect.height()
            painter.drawLine(
                QPointF(rect.left(), y), QPointF(rect.right(), y)
            )
            painter.setPen(QColor(MUTED))
            painter.drawText(
                QRectF(0, y - 7, 22, 14),
                Qt.AlignmentFlag.AlignRight, str(value),
            )
            painter.setPen(QPen(QColor("#EEEAF5"), 1))

        points = []
        for index, value in enumerate(self.values):
            x = rect.left() + rect.width() * index / max(
                1, len(self.values) - 1
            )
            y = rect.bottom() - value / 100 * rect.height()
            points.append(QPointF(x, y))

        if len(points) >= 2:
            polygon = [QPointF(points[0].x(), rect.bottom())]
            polygon.extend(points)
            polygon.append(QPointF(points[-1].x(), rect.bottom()))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(121, 87, 232, 30))
            painter.drawPolygon(QPolygonF(polygon))

        painter.setPen(QPen(QColor(PURPLE), 3))
        for index in range(len(points) - 1):
            painter.drawLine(points[index], points[index + 1])

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(PURPLE))
        for point in points:
            painter.drawEllipse(point, 4, 4)

        painter.setPen(QColor(MUTED))
        painter.setFont(QFont("Segoe UI", 8))
        for index in range(len(self.values)):
            x = rect.left() + rect.width() * index / max(
                1, len(self.values) - 1
            )
            painter.drawText(
                QRectF(x - 28, rect.bottom() + 7, 56, 16),
                Qt.AlignmentFlag.AlignHCenter, f"Week {index + 1}",
            )


# ---------------------------------------------------------
# Main Home View
# ---------------------------------------------------------

class HomeView(QWidget):
    play_requested = pyqtSignal()

    # Emits a category ID so the main window can open Games.
    category_requested = pyqtSignal(str)

    # Emits when any Explore games button is clicked.
    games_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user_id = None
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"background: {BG};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 10, 12, 10)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: #EEEAF7; width: 8px; margin: 2px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #C9B9F4; min-height: 25px;
                border-radius: 4px;
            }
        """)
        outer.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        scroll.setWidget(content)

        page = QVBoxLayout(content)
        page.setContentsMargins(2, 2, 8, 10)
        page.setSpacing(14)

        # Header row
        header_row = QHBoxLayout()
        title_column = QVBoxLayout()
        title_column.setSpacing(4)
        title_column.addWidget(
            make_label("Your RehabQuest Adventure", 21, DARK, True)
        )
        subtitle = make_label(
            "Interactive rehabilitation powered by your movements.",
            10, MUTED,
        )
        subtitle.setWordWrap(True)
        title_column.addWidget(subtitle)
        header_row.addLayout(title_column, 1)

        self.date_card = self._make_info_card(
            "📅", "TODAY", date.today().strftime("%b %d, %Y"), PURPLE
        )
        header_row.addWidget(self.date_card)

        self.streak_card = self._make_info_card(
            "🔥", "CURRENT STREAK", "0 Days", ORANGE
        )
        header_row.addWidget(self.streak_card)

        header_row.addWidget(self._make_level_card())
        page.addLayout(header_row)

        # Hero
        self.hero = DashboardHeroCard(self)
        self.hero.setMinimumHeight(205)
        self.hero.play_now_clicked.connect(self.play_requested.emit)
        page.addWidget(self.hero)

        # Exercise categories
        category_heading = QHBoxLayout()
        category_heading.addWidget(
            make_label("Choose an Exercise Category", 15, DARK, True)
        )
        category_heading.addStretch()
        category_heading.addWidget(
            make_label("4 TRAINING ZONES", 9, PURPLE, True)
        )
        page.addLayout(category_heading)

        category_grid = QGridLayout()
        category_grid.setSpacing(12)

        categories = [
            (
                "wrist_hand", "🎯", "Wrist & Hand",
                "Wrist • Fingers • Hand",
                "Reach, point and practise hand control.",
                PURPLE, LAVENDER,
            ),
            (
                "shoulder_elbow", "💪", "Shoulder & Elbow",
                "Shoulder • Arm • Elbow",
                "Build controlled arm-reaching movements.",
                TEAL, TEAL_LIGHT,
            ),
            (
                "knee_lower_limb", "👣", "Knee & Lower Limb",
                "Knee • Leg • Stepping",
                "Practise knee lifts and stepping tasks.",
                ORANGE, ORANGE_LIGHT,
            ),
            (
                "trunk_posture", "🧍", "Trunk & Posture",
                "Trunk • Balance • Stability",
                "Work on posture and controlled movement.",
                PINK, PINK_LIGHT,
            ),
        ]

        for column, data in enumerate(categories):
            category = ExerciseCategoryCard(*data)
            category.category_clicked.connect(
                self._on_explore_games_clicked
            )
            category_grid.addWidget(category, 0, column)

        page.addLayout(category_grid)

        # Performance metrics
        performance_heading = QHBoxLayout()
        performance_heading.addWidget(
            make_label("Today's Performance", 15, DARK, True)
        )
        performance_heading.addStretch()
        performance_heading.addWidget(
            make_label("LIVE DATA WHEN CONNECTED", 8, PURPLE, True)
        )
        page.addLayout(performance_heading)

        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(11)

        self.metric_cards = [
            PerformanceMetricCard(
                "🏆", "MOVEMENT SCORE", "--",
                "Waiting for session data", PURPLE,
            ),
            PerformanceMetricCard(
                "🎯", "ACCURACY", "--",
                "Target accuracy", TEAL,
            ),
            PerformanceMetricCard(
                "↗", "RANGE OF MOTION", "--",
                "Joint movement", ORANGE,
            ),
            PerformanceMetricCard(
                "⏱", "SESSION TIME", "--",
                "Exercise duration", PINK,
            ),
        ]

        for column, card in enumerate(self.metric_cards):
            metrics_grid.addWidget(card, 0, column)

        page.addLayout(metrics_grid)

        # Activity and progress
        bottom_grid = QGridLayout()
        bottom_grid.setSpacing(12)

        self.weekly = WeeklyActivityCard(self)
        bottom_grid.addWidget(self.weekly, 0, 0)

        progress_card = make_card()
        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setContentsMargins(16, 14, 16, 14)
        progress_layout.setSpacing(7)

        progress_header = QHBoxLayout()
        progress_header.addWidget(
            make_label("Progress Overview", 13, DARK, True)
        )
        progress_header.addStretch()
        progress_header.addWidget(
            make_label("RECENT WEEKS", 8, PURPLE, True)
        )
        progress_layout.addLayout(progress_header)

        progress_layout.addWidget(
            make_label(
                "Illustrative trend until real session scores are connected.",
                9, MUTED,
            )
        )
        progress_layout.addWidget(
            ProgressTrendChart([46, 62, 76, 87])
        )

        self.progress_summary = make_label(
            "Complete a session to start tracking your progress.",
            9, TEAL, True,
        )
        self.progress_summary.setWordWrap(True)
        progress_layout.addWidget(self.progress_summary)

        bottom_grid.addWidget(progress_card, 0, 1)
        bottom_grid.setColumnStretch(0, 1)
        bottom_grid.setColumnStretch(1, 1)
        page.addLayout(bottom_grid)

        footer = make_label(
            "RehabQuest is a rehabilitation-support prototype. "
            "Follow appropriate exercises and professional guidance.",
            9, MUTED,
        )
        footer.setWordWrap(True)
        page.addWidget(footer)

    def _make_info_card(self, icon, title, value, accent):
        card = make_card()
        card.setMinimumWidth(115)
        card.setMaximumWidth(175)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(11, 9, 11, 9)
        layout.setSpacing(5)

        top = QHBoxLayout()
        top.addWidget(make_label(icon, 14, accent, True))
        top.addWidget(make_label(title, 8, MUTED, True))
        layout.addLayout(top)

        value_label = make_label(value, 11, DARK, True)
        value_label.setObjectName("infoValue")
        layout.addWidget(value_label)

        return card

    def _make_level_card(self):
        card = make_card()
        card.setMinimumWidth(135)
        card.setMaximumWidth(185)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(11, 9, 11, 9)
        layout.setSpacing(5)

        layout.addWidget(
            make_label("🏆  LEVEL 1", 10, PURPLE, True)
        )

        self.xp_label = make_label("0 / 500 XP", 9, MUTED)
        layout.addWidget(self.xp_label)

        self.xp_bar = QProgressBar()
        self.xp_bar.setRange(0, 500)
        self.xp_bar.setValue(0)
        self.xp_bar.setTextVisible(False)
        self.xp_bar.setFixedHeight(7)
        self.xp_bar.setStyleSheet("""
            QProgressBar {
                background: #E9E4F5; border: none; border-radius: 3px;
            }
            QProgressBar::chunk {
                background: #7957E8; border-radius: 3px;
            }
        """)
        layout.addWidget(self.xp_bar)

        return card

    def _on_explore_games_clicked(self, category_id):
        """Request navigation to Games and pass the selected category."""
        self.category_requested.emit(category_id)
        self.games_requested.emit()

    def refresh_for_user(self, user_id, name="Patient"):
        self._user_id = user_id

        streak = get_current_streak(user_id)
        self.hero.set_user(name, streak)
        self.weekly.set_sessions(
            get_weekly_session_days(user_id)
        )

        streak_label = self.streak_card.findChild(
            QLabel, "infoValue"
        )
        if streak_label:
            streak_label.setText(f"{streak} Days")

        # Refresh the daily quote data, retaining compatibility with local_data.
        get_random_quote()

    def set_xp_progress(self, current_xp, xp_goal=500):
        xp_goal = max(1, int(xp_goal))
        current_xp = max(0, min(int(current_xp), xp_goal))

        self.xp_bar.setRange(0, xp_goal)
        self.xp_bar.setValue(current_xp)
        self.xp_label.setText(
            f"{current_xp} / {xp_goal} XP"
        )

    def set_performance_metrics(
        self,
        score=None,
        accuracy=None,
        range_of_motion=None,
        session_time=None,
    ):
        values = [
            score if score is not None else "--",
            accuracy if accuracy is not None else "--",
            range_of_motion if range_of_motion is not None else "--",
            session_time if session_time is not None else "--",
        ]

        for card, value in zip(self.metric_cards, values):
            card.value_label.setText(str(value))
