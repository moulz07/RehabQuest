
"""
Decorative Shapes
-----------------
Small, stateless drawing helpers used across screens so the visual motifs
stay consistent and polished.
"""

import math
import random

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import (
    QColor,
    QPainterPath,
    QPen,
    QRadialGradient,
)


def draw_flower(
    painter,
    cx,
    cy,
    size,
    hue,
    alpha=190,
    center_hue="#E8B84B",
):
    """Draw a simple six-petal flower centered at (cx, cy)."""
    if size <= 0:
        return

    petal_color = QColor(hue)
    petal_color.setAlpha(max(0, min(255, int(alpha))))

    center_color = QColor(center_hue)
    center_color.setAlpha(
        max(0, min(255, int(alpha) + 40))
    )

    petals = 6
    petal_w = size * 0.55
    petal_h = size * 1.0

    painter.save()
    try:
        painter.translate(cx, cy)

        for i in range(petals):
            angle = (360 / petals) * i

            painter.save()
            try:
                painter.rotate(angle)
                painter.setBrush(petal_color)
                painter.setPen(Qt.PenStyle.NoPen)

                rect = QRectF(
                    -petal_w / 2,
                    -petal_h,
                    petal_w,
                    petal_h * 0.62,
                )
                painter.drawEllipse(rect)
            finally:
                painter.restore()

        painter.setBrush(center_color)
        painter.setPen(Qt.PenStyle.NoPen)

        radius = size * 0.18
        painter.drawEllipse(
            QPointF(0, 0),
            radius,
            radius,
        )
    finally:
        painter.restore()


def draw_flower_with_stem(
    painter,
    base_x,
    base_y,
    height,
    flower_size,
    hue,
    stem_color="#8FBF8A",
    sway=0.0,
    leaf=True,
):
    """Draw a curved flower stem, optional leaf, and flower."""
    if height <= 0 or flower_size <= 0:
        return

    tip_x = base_x + sway
    tip_y = base_y - height

    painter.save()
    try:
        stem_pen = QPen(QColor(stem_color))
        stem_pen.setWidthF(2.4)
        stem_pen.setCapStyle(
            Qt.PenCapStyle.RoundCap
        )
        painter.setPen(stem_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        path = QPainterPath()
        path.moveTo(base_x, base_y)

        ctrl_x = base_x + sway * 0.6
        path.cubicTo(
            QPointF(ctrl_x, base_y - height * 0.4),
            QPointF(tip_x, base_y - height * 0.75),
            QPointF(tip_x, tip_y),
        )
        painter.drawPath(path)

        if leaf:
            leaf_color = QColor(stem_color)
            leaf_color.setAlpha(190)

            painter.setBrush(leaf_color)
            painter.setPen(Qt.PenStyle.NoPen)

            mid_x = base_x + sway * 0.3
            mid_y = base_y - height * 0.42

            painter.save()
            try:
                painter.translate(mid_x, mid_y)
                painter.rotate(-35)
                painter.drawEllipse(
                    QRectF(-2, -10, 14, 7)
                )
            finally:
                painter.restore()

        draw_flower(
            painter,
            tip_x,
            tip_y,
            flower_size,
            hue,
        )
    finally:
        painter.restore()


def draw_star_field(
    painter,
    rect_w,
    rect_h,
    count=18,
    seed=3,
    t=0.0,
    color=QColor(255, 255, 255),
    offset_x=0.0,
    offset_y=0.0,
):
    """Draw a deterministic field of softly twinkling stars."""
    if rect_w <= 0 or rect_h <= 0 or count <= 0:
        return

    # Re-seeding keeps star positions consistent between repaints.
    rng = random.Random(seed)

    painter.save()
    try:
        painter.setPen(Qt.PenStyle.NoPen)

        for _ in range(count):
            x = rng.uniform(0.0, 1.0) * rect_w + offset_x
            y = rng.uniform(0.0, 1.0) * rect_h + offset_y

            phase = rng.uniform(0, math.tau)
            speed = rng.uniform(0.6, 1.6)

            twinkle = 0.5 + 0.5 * math.sin(
                t * speed + phase
            )

            radius = rng.uniform(1.0, 2.2) * (
                0.8 + 0.4 * twinkle
            )

            star_color = QColor(color)
            star_color.setAlpha(
                int(70 + 130 * twinkle)
            )

            painter.setBrush(star_color)
            painter.drawEllipse(
                QPointF(x, y),
                radius,
                radius,
            )
    finally:
        painter.restore()


def draw_constellation(
    painter,
    points,
    edges,
    t=0.0,
    line_color=QColor(150, 160, 210, 90),
    node_color=QColor(225, 228, 255, 230),
):
    """Draw connecting lines and softly glowing constellation nodes."""
    if not points:
        return

    painter.save()
    try:
        line_pen = QPen(line_color)
        line_pen.setWidthF(1.1)
        painter.setPen(line_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        for a, b in edges:
            if (
                isinstance(a, int)
                and isinstance(b, int)
                and 0 <= a < len(points)
                and 0 <= b < len(points)
            ):
                painter.drawLine(points[a], points[b])

        painter.setPen(Qt.PenStyle.NoPen)

        for i, point in enumerate(points):
            pulse = 0.5 + 0.5 * math.sin(
                t * 1.4 + i
            )
            glow_radius = 10 + 4 * pulse

            glow = QRadialGradient(
                point,
                glow_radius,
            )

            inner_color = QColor(node_color)
            inner_color.setAlpha(
                int(70 * pulse) + 20
            )

            outer_color = QColor(node_color)
            outer_color.setAlpha(0)

            glow.setColorAt(0, inner_color)
            glow.setColorAt(1, outer_color)

            painter.setBrush(glow)
            painter.drawEllipse(
                point,
                glow_radius,
                glow_radius,
            )

            painter.setBrush(node_color)
            painter.drawEllipse(
                point,
                3.0,
                3.0,
            )
    finally:
        painter.restore()
