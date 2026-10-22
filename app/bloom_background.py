"""
Bloom Background
------------------
Light lavender/periwinkle gradient background with subtle animations.
"""

import math
import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPainterPath, QRadialGradient

from decorative_shapes import draw_star_field


class BloomPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._t = 0.0
        self._clock = QTimer(self)
        self._clock.timeout.connect(self._tick)

        rng = random.Random(9)
        self._particles = [
            {
                "x": rng.uniform(0.0, 1.0),
                "y": rng.uniform(0.0, 0.75),
                "r": rng.uniform(2.0, 4.0),
                "phase": rng.uniform(0, math.tau),
                "dx": rng.uniform(-0.012, 0.012),
                "dy": rng.uniform(-0.012, -0.003),
                "tint": rng.choice(["#C9B7EC", "#E3B6D6", "#B8A3EF"]),
            }
            for _ in range(16)
        ]

    def showEvent(self, event):
        self._clock.start(40)
        super().showEvent(event)

    def hideEvent(self, event):
        self._clock.stop()
        super().hideEvent(event)

    def _tick(self):
        self._t += 0.04
        self.update()

    def paintEvent(self, event):
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        self._draw_wash(painter, w, h)
        self._draw_sparkles(painter, w, h)
        self._draw_particles(painter, w, h)
        self.draw_foreground(painter, w, h)

    def draw_foreground(self, painter, w, h):
        pass

    def _draw_wash(self, painter, w, h):
        gradient = QLinearGradient(0, 0, w * 0.4, h)
        gradient.setColorAt(0.0, QColor("#E3DBF8"))
        gradient.setColorAt(0.5, QColor("#EDE5F8"))
        gradient.setColorAt(1.0, QColor("#F8F2F8"))
        painter.fillRect(0, 0, w, h, gradient)

    def _draw_sparkles(self, painter, w, h):
        draw_star_field(
            painter, w, h * 0.7, count=24, seed=11, t=self._t,
            color=QColor(150, 130, 200),
        )

    def _draw_particles(self, painter, w, h):
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self._particles:
            x = (p["x"] + p["dx"] * self._t) % 1.0
            y = (p["y"] + p["dy"] * self._t) % 1.0
            pulse = 0.5 + 0.5 * math.sin(self._t * 0.7 + p["phase"])
            cx, cy = x * w, y * h
            r = p["r"] * (0.85 + 0.3 * pulse)

            glow = QRadialGradient(QPointF(cx, cy), r * 3.0)
            c1 = QColor(p["tint"])
            c1.setAlpha(int(45 + 35 * pulse))
            c2 = QColor(p["tint"])
            c2.setAlpha(0)
            glow.setColorAt(0.0, c1)
            glow.setColorAt(1.0, c2)
            painter.setBrush(glow)
            painter.drawEllipse(QPointF(cx, cy), r * 3.0, r * 3.0)
