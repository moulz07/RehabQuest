
"""
Games View for RehabQuest
-------------------------
Four expandable rehabilitation categories with two simple games each.
Reach & Collect retains its existing game launch ID.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QLinearGradient


PURPLE = "#7E5BE8"
DARK_PURPLE = "#2F2154"
MUTED_PURPLE = "#7A6C9B"


# ---------------------------------------------------------
# GAME CARD
# ---------------------------------------------------------

class GameCard(QFrame):
    start_clicked = pyqtSignal(str)

    def __init__(
        self,
        game_id,
        icon,
        title,
        tag,
        description,
        button_text,
        is_primary=True,
        parent=None,
    ):
        super().__init__(parent)

        self.game_id = game_id
        self.is_primary = is_primary

        self.setMinimumSize(240, 250)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )

        self._build_ui(
            icon, title, tag, description, button_text
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        gradient = QLinearGradient(
            0, 0, 0, self.height()
        )

        if self.is_primary:
            gradient.setColorAt(0, QColor("#FFFFFF"))
            gradient.setColorAt(1, QColor("#F4EEFB"))
        else:
            gradient.setColorAt(0, QColor("#FBF9FD"))
            gradient.setColorAt(1, QColor("#EDE7F6"))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(self.rect(), 18, 18)

        super().paintEvent(event)

    def _build_ui(
        self, icon, title, tag, description, button_text
    ):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(9)

        top = QHBoxLayout()

        icon_label = QLabel(icon)
        icon_label.setStyleSheet(
            "font-size: 24px; background: transparent;"
        )
        top.addWidget(icon_label)
        top.addStretch()

        tag_label = QLabel(tag)
        tag_label.setStyleSheet(f"""
            color: {PURPLE if self.is_primary else "#9A73C9"};
            background: rgba(126, 91, 232, 25);
            border-radius: 7px;
            padding: 4px 7px;
            font-size: 9px;
            font-weight: bold;
        """)
        top.addWidget(tag_label)
        layout.addLayout(top)

        title_label = QLabel(title)
        title_font = QFont("Segoe UI", 13)
        title_font.setWeight(QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(
            f"color: {DARK_PURPLE}; background: transparent;"
        )
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            color: #6C5D8C;
            font-size: 11px;
            background: transparent;
        """)
        layout.addWidget(desc_label)

        layout.addStretch()

        button = QPushButton(button_text)
        button.setMinimumHeight(38)
        button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        button.setStyleSheet("""
            QPushButton {
                background: #7E5BE8;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 7px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #8E6BF8;
            }
            QPushButton:disabled {
                background: #EAE4F2;
                color: #8C80A4;
            }
        """)

        if self.is_primary:
            button.clicked.connect(
                lambda checked=False:
                self.start_clicked.emit(self.game_id)
            )
        else:
            button.setEnabled(False)

        layout.addWidget(button)


# ---------------------------------------------------------
# EXPANDABLE EXERCISE CATEGORY
# ---------------------------------------------------------

class ExerciseCategory(QFrame):
    game_selected = pyqtSignal(str)
    expanded_changed = pyqtSignal(object, bool)

    def __init__(
        self,
        title,
        icon,
        description,
        games,
        parent=None,
    ):
        super().__init__(parent)

        self.category_title = title
        self.category_icon = icon
        self.expanded = False

        self.setObjectName("ExerciseCategory")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )

        self.setStyleSheet("""
            QFrame#ExerciseCategory {
                background: #F7F3FC;
                border: 1px solid #E6DDF5;
                border-radius: 17px;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(15, 14, 15, 14)
        root.setSpacing(9)

        self.toggle_button = QPushButton(
            f"{icon}   {title}   ▾"
        )
        self.toggle_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.toggle_button.setMinimumHeight(42)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                color: #2F2154;
                background: transparent;
                border: none;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
                padding: 4px;
            }
            QPushButton:hover {
                color: #7E5BE8;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle)
        root.addWidget(self.toggle_button)

        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("""
            color: #7A6C9B;
            background: transparent;
            border: none;
            font-size: 11px;
        """)
        root.addWidget(description_label)

        self.games_container = QWidget()
        self.games_container.setStyleSheet(
            "background: transparent; border: none;"
        )

        games_layout = QVBoxLayout(self.games_container)
        games_layout.setContentsMargins(0, 5, 0, 0)
        games_layout.setSpacing(10)

        for game in games:
            card = GameCard(
                game_id=game["id"],
                icon=game["icon"],
                title=game["title"],
                tag=game["status"],
                description=game["description"],
                button_text=game["button"],
                is_primary=game.get("active", False),
            )

            card.start_clicked.connect(
                self.game_selected.emit
            )
            games_layout.addWidget(card)

        root.addWidget(self.games_container)
        self.games_container.hide()

    def toggle(self):
        self.expanded_changed.emit(
            self, not self.expanded
        )

    def set_expanded(self, expanded):
        self.expanded = expanded
        self.games_container.setVisible(expanded)

        arrow = "▴" if expanded else "▾"
        self.toggle_button.setText(
            f"{self.category_icon}   "
            f"{self.category_title}   {arrow}"
        )


# ---------------------------------------------------------
# MAIN GAMES VIEW
# ---------------------------------------------------------

class GamesView(QWidget):
    game_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.categories = []
        self._build_ui()

    def _build_ui(self):
        page = QVBoxLayout(self)
        page.setContentsMargins(10, 10, 10, 10)
        page.setSpacing(12)

        header = QLabel("Rehabilitation Exercises")
        font = QFont("Segoe UI", 18)
        font.setWeight(QFont.Weight.Bold)
        header.setFont(font)
        header.setStyleSheet(
            "color: #2F2154; background: transparent;"
        )
        page.addWidget(header)

        subtitle = QLabel(
            "Choose a body area and explore its rehabilitation games."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("""
            color: #7A6C9B;
            font-size: 12px;
            background: transparent;
        """)
        page.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #F2ECFA;
                width: 8px;
                margin: 2px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #C5B1EE;
                min-height: 25px;
                border-radius: 4px;
            }
        """)
        page.addWidget(scroll, 1)

        content = QWidget()
        content.setStyleSheet(
            "background: transparent;"
        )
        scroll.setWidget(content)

        grid = QGridLayout(content)
        grid.setContentsMargins(4, 5, 8, 10)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        categories_data = [
            {
                "title": "Wrist & Hand",
                "icon": "✋",
                "description": (
                    "Improve hand coordination, finger movement "
                    "and wrist reaching."
                ),
                "games": [
                    {
                        "id": "reach_and_collect",
                        "icon": "🎯",
                        "title": "Reach & Collect",
                        "status": "AVAILABLE",
                        "description": (
                            "Move your hand toward targets on the "
                            "screen and collect them using the "
                            "existing hand-tracking game."
                        ),
                        "button": "▶ Start Exercise",
                        "active": True,
                    },
                    {
                        "id": "finger_tap",
                        "icon": "👆",
                        "title": "Finger Tap Challenge",
                        "status": "PLANNED",
                        "description": (
                            "Touch or pinch virtual targets with "
                            "your fingers as they appear on screen."
                        ),
                        "button": "Coming Soon",
                    },
                ],
            },
            {
                "title": "Shoulder & Elbow",
                "icon": "💪",
                "description": (
                    "Practise arm raising, reaching and controlled "
                    "upper-limb movement."
                ),
                "games": [
                    {
                        "id": "sky_reach",
                        "icon": "☁️",
                        "title": "Sky Reach",
                        "status": "PLANNED",
                        "description": (
                            "Raise your tracked hand to reach "
                            "targets at different screen heights."
                        ),
                        "button": "Coming Soon",
                    },
                    {
                        "id": "rainbow_painter",
                        "icon": "🎨",
                        "title": "Rainbow Painter",
                        "status": "PLANNED",
                        "description": (
                            "Move your hand to follow a path and "
                            "draw colourful lines on the screen."
                        ),
                        "button": "Coming Soon",
                    },
                ],
            },
            {
                "title": "Knee & Lower Limb",
                "icon": "🦵",
                "description": (
                    "Practise knee lifting, stepping and "
                    "lower-limb movement."
                ),
                "games": [
                    {
                        "id": "knee_lift_quest",
                        "icon": "⬆️",
                        "title": "Knee Lift Quest",
                        "status": "PLANNED",
                        "description": (
                            "Lift one knee toward a target zone "
                            "detected using body landmarks."
                        ),
                        "button": "Coming Soon",
                    },
                    {
                        "id": "step_reach",
                        "icon": "👣",
                        "title": "Step & Reach",
                        "status": "PLANNED",
                        "description": (
                            "Alternate steps while reaching toward "
                            "visual targets in a guided sequence."
                        ),
                        "button": "Coming Soon",
                    },
                ],
            },
            {
                "title": "Trunk & Postural Stability",
                "icon": "🧍",
                "description": (
                    "Practise upright posture, trunk control "
                    "and balance-related movement."
                ),
                "games": [
                    {
                        "id": "balance_bubbles",
                        "icon": "🫧",
                        "title": "Balance Bubbles",
                        "status": "PLANNED",
                        "description": (
                            "Shift your upper body toward visual "
                            "targets to pop floating bubbles."
                        ),
                        "button": "Coming Soon",
                    },
                    {
                        "id": "posture_guardian",
                        "icon": "🛡️",
                        "title": "Posture Guardian",
                        "status": "PLANNED",
                        "description": (
                            "Keep your torso aligned with an "
                            "on-screen posture guide."
                        ),
                        "button": "Coming Soon",
                    },
                ],
            },
        ]

        for index, data in enumerate(categories_data):
            category = ExerciseCategory(
                title=data["title"],
                icon=data["icon"],
                description=data["description"],
                games=data["games"],
                parent=content,
            )

            category.game_selected.connect(
                self.game_selected.emit
            )
            category.expanded_changed.connect(
                self._on_category_toggled
            )

            self.categories.append(category)

            row, column = divmod(index, 2)
            grid.addWidget(category, row, column)

        for category in self.categories:
            category.set_expanded(False)

    def _on_category_toggled(
        self, selected_category, should_expand
    ):
        # Expand one category at a time.
        for category in self.categories:
            category.set_expanded(
                category is selected_category
                and should_expand
            )

    
    def open_category(self, category_id):
        """Expand the exercise category selected from the Home dashboard."""

        category_titles = {
            "wrist_hand": "Wrist & Hand",
            "shoulder_elbow": "Shoulder & Elbow",
            "knee_lower_limb": "Knee & Lower Limb",
            "trunk_posture": "Trunk & Postural Stability",
        }

        target_title = category_titles.get(category_id)

        if not target_title:
            return

        for category in self.categories:
            is_target = category.category_title == target_title
            category.set_expanded(is_target)

        self._on_category_toggled(None, True)

