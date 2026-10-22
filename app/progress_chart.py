"""
Progress Chart
----------------
Custom-drawn high-performance line chart widget using QPainter.
Shows rehabilitation metrics across sessions with clear axes and clean markers.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QPainterPath


class ProgressChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._history = []
        self._series = []
        self._y_max = 100
        self._y_suffix = ""
        self.setMinimumHeight(160)

    def load(self, history, series, y_max=100, y_suffix=""):
        self._history = history or []
        self._series = series or []
        self._y_suffix = y_suffix
        self._y_max = y_max if y_max is not None else self._auto_y_max()
        self.update()

    def _auto_y_max(self):
        values = []
        for entry in self._history:
            for s in self._series:
                v = entry.get(s["key"])
                if v is not None:
                    try:
                        values.append(float(v))
                    except (TypeError, ValueError):
                        pass
        if not values or max(values) <= 0:
            return 10
        return max(values) * 1.25

    def paintEvent(self, event):
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # Margins for axes
        pad_left = 42
        pad_right = 16
        pad_top = 16
        pad_bottom = 26
        chart_w = max(10, w - pad_left - pad_right)
        chart_h = max(10, h - pad_top - pad_bottom)

        # Draw gridlines and Y-axis labels
        grid_pen = QPen(QColor(180, 165, 220, 60))
        grid_pen.setWidthF(1.0)
        grid_pen.setStyle(Qt.PenStyle.DashLine)

        axis_font = QFont("Segoe UI", 9)
        painter.setFont(axis_font)

        y_steps = 4
        for i in range(y_steps + 1):
            y_val = (self._y_max / y_steps) * i
            y_pos = pad_top + chart_h - (chart_h / y_steps) * i

            painter.setPen(grid_pen)
            painter.drawLine(int(pad_left), int(y_pos), int(w - pad_right), int(y_pos))

            painter.setPen(QColor("#8C7EA8"))
            lbl = f"{int(y_val)}{self._y_suffix}"
            painter.drawText(QRectF(0, y_pos - 8, pad_left - 6, 16), Qt.AlignmentFlag.AlignRight, lbl)

        if not self._history:
            painter.setPen(QColor("#A093BC"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No sessions recorded yet")
            return

        n_pts = len(self._history)
        x_step = chart_w / max(1, n_pts - 1) if n_pts > 1 else chart_w / 2

        # Draw X-axis session labels
        for idx in range(n_pts):
            cx = pad_left + idx * x_step if n_pts > 1 else pad_left + chart_w / 2
            painter.setPen(QColor("#8C7EA8"))
            painter.drawText(QRectF(cx - 15, h - pad_bottom + 6, 30, 16), Qt.AlignmentFlag.AlignCenter, f"S{idx+1}")

        # Draw Series Lines & Markers
        for s in self._series:
            color = QColor(s.get("color", "#7C5CE0"))
            line_pen = QPen(color)
            line_pen.setWidthF(2.6)
            painter.setPen(line_pen)

            points = []
            for idx, entry in enumerate(self._history):
                v = entry.get(s["key"])
                if v is not None:
                    try:
                        fv = float(v)
                    except (TypeError, ValueError):
                        fv = 0.0
                    ratio = min(1.0, max(0.0, fv / max(0.001, self._y_max)))
                    px = pad_left + idx * x_step if n_pts > 1 else pad_left + chart_w / 2
                    py = pad_top + chart_h - (ratio * chart_h)
                    points.append(QPointF(px, py))

            if len(points) > 1:
                path = QPainterPath()
                path.moveTo(points[0])
                for pt in points[1:]:
                    path.lineTo(pt)
                painter.drawPath(path)

            # Markers
            for pt in points:
                painter.setBrush(QColor("#FFFFFF"))
                painter.setPen(line_pen)
                painter.drawEllipse(pt, 4.0, 4.0)
