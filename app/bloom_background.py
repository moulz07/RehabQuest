
"""
Bloom Background — RehabQuest
-----------------------------
Calm clinical-tech background featuring:
- Soft lavender, periwinkle, and white gradients
- Translucent flowing aurora ribbons
- Subtle motion-tracking nodes and connecting lines
- Slowly drifting ambient particles

Designed for RehabQuest's rehabilitation dashboard.
"""

import math
import random

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QLinearGradient,
    QPainterPath,
    QRadialGradient,
    QPen,
)


class BloomPage(QWidget):
    """Animated aurora-style background for RehabQuest pages."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._t = 0.0

        self._clock = QTimer(self)
        self._clock.setInterval(50)
        self._clock.timeout.connect(self._tick)

        rng = random.Random(21)

        self._particles = [
            {
                "x": rng.uniform(0.03, 0.97),
                "y": rng.uniform(0.04, 0.92),
                "radius": rng.uniform(1.5, 3.5),
                "phase": rng.uniform(0, math.tau),
                "speed": rng.uniform(0.4, 1.0),
                "drift": rng.uniform(-0.008, 0.008),
                "color": rng.choice([
                    "#B9A7F3",
                    "#C9B9EE",
                    "#E8C4E1",
                    "#AFC9F4",
                ]),
            }
            for _ in range(24)
        ]

        # Fixed normalized positions create a subtle tracking motif.
        self._tracking_points = [
            (0.70, 0.15),
            (0.79, 0.20),
            (0.87, 0.14),
            (0.91, 0.25),
            (0.81, 0.32),
            (0.72, 0.29),
        ]

        self._tracking_edges = [
            (0, 1),
            (1, 2),
            (2, 3),
            (1, 4),
            (4, 5),
            (5, 0),
        ]

        self.setAttribute(
            Qt.WidgetAttribute.WA_OpaquePaintEvent,
            True,
        )

    def showEvent(self, event):
        super().showEvent(event)
        self._clock.start()

    def hideEvent(self, event):
        self._clock.stop()
        super().hideEvent(event)

    def _tick(self):
        self._t += 0.05
        self.update()

    # -----------------------------------------------------
    # Main painting
    # -----------------------------------------------------

    def paintEvent(self, event):
        width = self.width()
        height = self.height()

        if width <= 0 or height <= 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        self._draw_background(painter, width, height)
        self._draw_aurora(painter, width, height)
        self._draw_particles(painter, width, height)
        self._draw_tracking_network(
            painter, width, height
        )

        # Allows subclasses to paint their own foreground elements.
        self.draw_foreground(painter, width, height)

        painter.end()

    def draw_foreground(self, painter, width, height):
        """Optional extension point for subclasses."""
        pass

    # -----------------------------------------------------
    # Base gradient and ambient lighting
    # -----------------------------------------------------

    def _draw_background(self, painter, width, height):
        gradient = QLinearGradient(
            0, 0, width * 0.75, height
        )

        gradient.setColorAt(
            0.0, QColor("#E3E8FF")
        )
        gradient.setColorAt(
            0.42, QColor("#F0E9FC")
        )
        gradient.setColorAt(
            0.75, QColor("#F8F0FA")
        )
        gradient.setColorAt(
            1.0, QColor("#FDF6F8")
        )

        painter.fillRect(
            QRectF(0, 0, width, height),
            gradient,
        )

        # Cool periwinkle glow near the top-right.
        self._draw_glow(
            painter,
            width * (0.83 + 0.015 * math.sin(self._t * 0.25)),
            height * 0.16,
            min(width, height) * 0.48,
            "#AEBDF8",
            48,
        )

        # Warm lilac-pink glow near the lower-left.
        self._draw_glow(
            painter,
            width * 0.08,
            height * 0.82,
            min(width, height) * 0.44,
            "#E9C5ED",
            35,
        )

    @staticmethod
    def _draw_glow(
        painter,
        cx,
        cy,
        radius,
        color,
        alpha,
    ):
        """Draw a large, soft radial light."""
        if radius <= 0:
            return

        glow = QRadialGradient(
            QPointF(cx, cy),
            radius,
        )

        center_color = QColor(color)
        center_color.setAlpha(alpha)

        transparent_color = QColor(color)
        transparent_color.setAlpha(0)

        glow.setColorAt(0.0, center_color)
        glow.setColorAt(1.0, transparent_color)

        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(
            QPointF(cx, cy),
            radius,
            radius,
        )
        painter.restore()

    # -----------------------------------------------------
    # Aurora waves
    # -----------------------------------------------------

    def _draw_aurora(self, painter, width, height):
        """
        Draw flowing translucent ribbons.

        The curves move gently over time without using expensive
        image effects or external assets.
        """
        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        wave_specs = [
            {
                "base": 0.25,
                "amplitude": 0.045,
                "phase": 0.0,
                "color": "#A9B9F2",
                "alpha": 35,
            },
            {
                "base": 0.32,
                "amplitude": 0.055,
                "phase": 1.8,
                "color": "#C6A9EC",
                "alpha": 30,
            },
            {
                "base": 0.39,
                "amplitude": 0.04,
                "phase": 3.3,
                "color": "#E9C1E7",
                "alpha": 27,
            },
        ]

        for spec in wave_specs:
            phase = spec["phase"] + self._t * 0.12

            start_y = (
                spec["base"]
                + spec["amplitude"] * math.sin(phase)
            ) * height

            end_y = (
                spec["base"]
                + spec["amplitude"]
                * math.sin(phase + 2.0)
            ) * height

            control_1 = QPointF(
                width * 0.28,
                start_y - height * 0.15,
            )

            control_2 = QPointF(
                width * 0.68,
                end_y + height * 0.14,
            )

            path = QPainterPath()
            path.moveTo(0, start_y)

            path.cubicTo(
                control_1,
                control_2,
                QPointF(width, end_y),
            )

            wave_color = QColor(spec["color"])
            wave_color.setAlpha(spec["alpha"])

            pen = QPen(wave_color)
            pen.setWidthF(
                max(1.0, min(width, height) * 0.002)
            )
            pen.setCapStyle(
                Qt.PenCapStyle.RoundCap
            )

            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

        # A faint curved ribbon across the lower portion.
        lower_path = QPainterPath()
        lower_path.moveTo(0, height * 0.77)

        lower_path.cubicTo(
            QPointF(
                width * 0.28,
                height * (
                    0.68 + 0.018 * math.sin(self._t * 0.25)
                ),
            ),
            QPointF(
                width * 0.68,
                height * (
                    0.88 + 0.018 * math.sin(self._t * 0.22)
                ),
            ),
            QPointF(width, height * 0.76),
        )

        lower_color = QColor("#D2C6F2")
        lower_color.setAlpha(24)

        lower_pen = QPen(lower_color)
        lower_pen.setWidthF(2.0)

        painter.setPen(lower_pen)
        painter.drawPath(lower_path)

        painter.restore()

    # -----------------------------------------------------
    # Floating particles
    # -----------------------------------------------------

    def _draw_particles(self, painter, width, height):
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)

        for particle in self._particles:
            drift = (
                particle["drift"]
                * math.sin(
                    self._t * particle["speed"]
                    + particle["phase"]
                )
            )

            x = (
                particle["x"] + drift
            ) * width

            y = (
                particle["y"]
                + 0.006
                * math.sin(
                    self._t * 0.35
                    + particle["phase"]
                )
            ) * height

            pulse = 0.5 + 0.5 * math.sin(
                self._t * particle["speed"]
                + particle["phase"]
            )

            radius = particle["radius"] * (
                0.85 + 0.3 * pulse
            )

            color = QColor(particle["color"])
            color.setAlpha(
                int(45 + 45 * pulse)
            )

            painter.setBrush(color)
            painter.drawEllipse(
                QPointF(x, y),
                radius,
                radius,
            )

        painter.restore()

    # -----------------------------------------------------
    # Subtle tracking network
    # -----------------------------------------------------

    def _draw_tracking_network(
        self,
        painter,
        width,
        height,
    ):
        """
        Draw a low-contrast landmark network inspired by
        markerless body and hand tracking.
        """
        points = [
            QPointF(
                x * width,
                y * height
                + math.sin(
                    self._t * 0.35 + index
                ) * 3.0,
            )
            for index, (x, y) in enumerate(
                self._tracking_points
            )
        ]

        painter.save()

        # Fine connecting lines.
        line_color = QColor("#8F9FDB")
        line_color.setAlpha(30)

        line_pen = QPen(line_color)
        line_pen.setWidthF(1.0)

        painter.setPen(line_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        for start, end in self._tracking_edges:
            painter.drawLine(
                points[start],
                points[end],
            )

        # Small glowing landmark nodes.
        painter.setPen(Qt.PenStyle.NoPen)

        for index, point in enumerate(points):
            pulse = 0.5 + 0.5 * math.sin(
                self._t * 0.9 + index
            )

            radius = 2.0 + pulse * 1.1

            node_color = QColor("#8999E1")
            node_color.setAlpha(
                int(45 + 30 * pulse)
            )

            painter.setBrush(node_color)
            painter.drawEllipse(
                point,
                radius,
                radius,
            )

        painter.restore()
