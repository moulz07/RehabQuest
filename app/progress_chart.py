
"""
Progress Chart
--------------
Custom-drawn rehabilitation progress chart for RehabQuest.

Displays movement-performance metrics across completed sessions:
- Overall movement score
- Trajectory accuracy
- Range of Motion (ROM)
- Movement speed
- Movement smoothness
- Reaction time
- Compensatory movement

Uses actual session-history values supplied by the dashboard.
Metrics with different units should be displayed in separate charts.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QFont,
    QPen,
    QPainterPath,
)


class ProgressChart(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._history = []
        self._series = []
        self._y_max = 100
        self._y_min = 0
        self._y_suffix = ""
        self._chart_title = "Rehabilitation Progress"
        self._x_label_prefix = "S"
        self._show_legend = True

        self.setMinimumHeight(200)

    def load(
        self,
        history,
        series,
        y_max=None,
        y_suffix="",
        y_min=0,
        title="Rehabilitation Progress",
        x_label_prefix="S",
        show_legend=True,
    ):
        """
        Load real session data into the chart.

        history:
            List of session dictionaries, ordered chronologically.

        series:
            List of metric definitions, for example:
            [
                {
                    "key": "accuracy",
                    "label": "Trajectory Accuracy",
                    "color": "#7C5CE0"
                }
            ]

        y_max / y_min:
            Explicit scale bounds. If y_max is None, it is calculated
            from the available numeric values.

        y_suffix:
            Optional axis suffix, e.g. "%" or "s".
            Only use a suffix when every displayed metric shares
            the same unit.
        """
        self._history = history or []
        self._series = series or []
        self._y_min = y_min
        self._y_suffix = y_suffix
        self._chart_title = title
        self._x_label_prefix = x_label_prefix
        self._show_legend = show_legend

        self._y_max = (
            y_max if y_max is not None else self._auto_y_max()
        )

        if self._y_max <= self._y_min:
            self._y_max = self._y_min + 1

        self.update()

    @staticmethod
    def _number(value):
        """Return a numeric value, or None for missing/invalid data."""
        if value is None:
            return None

        try:
            result = float(value)
        except (TypeError, ValueError):
            return None

        return result if result == result else None

    def _auto_y_max(self):
        values = []

        for entry in self._history:
            for metric in self._series:
                value = self._number(entry.get(metric["key"]))
                if value is not None:
                    values.append(value)

        if not values:
            return 100

        highest = max(values)

        if highest <= 0:
            return 1

        return highest * 1.15

    def _draw_text(
        self,
        painter,
        text,
        x,
        y,
        width,
        height,
        alignment=Qt.AlignmentFlag.AlignLeft,
    ):
        painter.drawText(
            QRectF(x, y, width, height),
            alignment,
            str(text),
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = self.width()
        h = self.height()

        # Background
        painter.fillRect(self.rect(), QColor("#FFFFFF"))

        if not self._history or not self._series:
            painter.setPen(QColor("#8C7EA8"))
            painter.setFont(QFont("Segoe UI", 10))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "No rehabilitation session data available",
            )
            return

        # Layout
        pad_left = 48
        pad_right = 18
        pad_top = 42
        pad_bottom = 34
        legend_height = 30 if self._show_legend else 0

        chart_w = max(10, w - pad_left - pad_right)
        chart_h = max(
            10,
            h - pad_top - pad_bottom - legend_height,
        )

        chart_bottom = pad_top + chart_h

        # Title
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        painter.setPen(QColor("#34264D"))
        self._draw_text(
            painter,
            self._chart_title,
            pad_left,
            8,
            chart_w,
            24,
        )

        # Axes and grid
        painter.setFont(QFont("Segoe UI", 8))
        grid_pen = QPen(QColor("#E9E3F2"))
        grid_pen.setWidthF(1)

        y_steps = 4
        y_range = self._y_max - self._y_min

        for i in range(y_steps + 1):
            ratio = i / y_steps
            value = self._y_min + y_range * ratio
            y = chart_bottom - chart_h * ratio

            painter.setPen(grid_pen)
            painter.drawLine(
                int(pad_left),
                int(y),
                int(w - pad_right),
                int(y),
            )

            painter.setPen(QColor("#8C7EA8"))
            label = f"{value:.0f}{self._y_suffix}"

            self._draw_text(
                painter,
                label,
                0,
                y - 8,
                pad_left - 8,
                16,
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter,
            )

        # Session positions
        count = len(self._history)

        if count == 1:
            x_positions = [pad_left + chart_w / 2]
        else:
            x_positions = [
                pad_left + i * chart_w / (count - 1)
                for i in range(count)
            ]

        # Session labels
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor("#8C7EA8"))

        for index, x in enumerate(x_positions):
            session = self._history[index].get(
                "session_label",
                f"{self._x_label_prefix}{index + 1}",
            )

            self._draw_text(
                painter,
                session,
                x - 22,
                chart_bottom + 7,
                44,
                16,
                Qt.AlignmentFlag.AlignCenter,
            )

        # Metric lines
        for metric in self._series:
            color = QColor(metric.get("color", "#7C5CE0"))
            line_pen = QPen(color)
            line_pen.setWidthF(2.4)
            line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

            painter.setPen(line_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            path = QPainterPath()
            segment_started = False
            points = []

            for index, entry in enumerate(self._history):
                value = self._number(entry.get(metric["key"]))

                # Missing values remain missing; they are not plotted as zero.
                if value is None:
                    segment_started = False
                    continue

                ratio = (value - self._y_min) / y_range
                ratio = max(0.0, min(1.0, ratio))

                x = x_positions[index]
                y = chart_bottom - ratio * chart_h
                point = QPointF(x, y)

                points.append(point)

                if not segment_started:
                    path.moveTo(point)
                    segment_started = True
                else:
                    path.lineTo(point)

            painter.drawPath(path)

            # Markers
            for point in points:
                painter.setPen(line_pen)
                painter.setBrush(QColor("#FFFFFF"))
                painter.drawEllipse(point, 4.0, 4.0)

        # Legend
        if self._show_legend:
            legend_y = h - 15
            legend_x = pad_left

            painter.setFont(QFont("Segoe UI", 8))

            for metric in self._series:
                color = QColor(metric.get("color", "#7C5CE0"))
                label = metric.get("label", metric["key"])

                painter.setPen(QPen(color, 2.4))
                painter.drawLine(
                    int(legend_x),
                    int(legend_y),
                    int(legend_x + 14),
                    int(legend_y),
                )

                painter.setPen(QColor("#625675"))
                self._draw_text(
                    painter,
                    label,
                    legend_x + 19,
                    legend_y - 9,
                    120,
                    18,
                )

                legend_x += 150

                # Avoid drawing legend entries beyond the widget.
                if legend_x > w - 110:
                    break

        painter.end()
