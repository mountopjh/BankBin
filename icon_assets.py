"""High-performance vector icon generation system for BankBin.

Renders crisp, multi-resolution, modern icons entirely with PyQt6 QPainter.
Supports dynamic state changes, DPI scaling (16px to 256px), and consistent
fintech aesthetic across taskbar, system tray, menus, dialogs, and panels.
"""

from __future__ import annotations

import math
from typing import Callable, Dict, Tuple

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
)

# Brand Color Palette
COLOR_PRIMARY = "#007ACC"
COLOR_PRIMARY_DARK = "#005A9E"
COLOR_PRIMARY_LIGHT = "#1C97EA"
COLOR_ACCENT = "#2563EB"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#EF4444"
COLOR_SLATE = "#475569"
COLOR_SLATE_LIGHT = "#64748B"
COLOR_MUTED = "#94A3B8"
COLOR_GOLD = "#F59E0B"

# Cache for generated QIcons: (name, kwargs_tuple) -> QIcon
_ICON_CACHE: Dict[Tuple, QIcon] = {}


def _create_painter(pixmap: QPixmap) -> QPainter:
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
    return painter


def _render_multi_size_icon(
    draw_fn: Callable[[QPainter, int, dict], None],
    sizes: Tuple[int, ...] = (16, 20, 24, 32, 48, 64, 128),
    **kwargs,
) -> QIcon:
    """Render a QIcon containing multiple pixmap sizes for flawless DPI scaling."""
    icon = QIcon()
    for size in sizes:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = _create_painter(pixmap)
        try:
            draw_fn(painter, size, kwargs)
        finally:
            painter.end()
        icon.addPixmap(pixmap)
    return icon


# =========================================================================
# 1. Main BankBin Application Badge & System Tray Icon
# =========================================================================


def _draw_app_badge(painter: QPainter, size: int, options: dict) -> None:
    active = options.get("active", True)
    show_status_dot = options.get("show_status_dot", False)

    s = float(size)
    pad = s * 0.04
    box_rect = QRectF(pad, pad, s - 2 * pad, s - 2 * pad)
    radius = s * 0.22

    # Background gradient
    grad = QLinearGradient(box_rect.topLeft(), box_rect.bottomRight())
    if active:
        grad.setColorAt(0.0, QColor("#1E88E5"))
        grad.setColorAt(0.5, QColor("#0D6EFD"))
        grad.setColorAt(1.0, QColor("#0A58CA"))
    else:
        grad.setColorAt(0.0, QColor("#64748B"))
        grad.setColorAt(1.0, QColor("#334155"))

    painter.setBrush(QBrush(grad))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(box_rect, radius, radius)

    # Subtle inner highlight ring
    highlight_pen = QPen(QColor(255, 255, 255, 45 if active else 25))
    highlight_pen.setWidthF(max(1.0, s * 0.03))
    painter.setPen(highlight_pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    inner_pad = highlight_pen.widthF() / 2.0 + pad
    painter.drawRoundedRect(
        QRectF(inner_pad, inner_pad, s - 2 * inner_pad, s - 2 * inner_pad),
        max(1.0, radius - 1),
        max(1.0, radius - 1),
    )

    # Stylized Bank Card body
    card_w = s * 0.68
    card_h = s * 0.44
    card_x = (s - card_w) / 2.0
    card_y = (s - card_h) / 2.0 - (s * 0.02 if show_status_dot else 0.0)
    card_r = max(1.5, s * 0.06)

    # Card shadow
    shadow_rect = QRectF(card_x, card_y + s * 0.025, card_w, card_h)
    painter.setBrush(QColor(0, 0, 0, 35))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(shadow_rect, card_r, card_r)

    # Card background (white frosted / pearlescent)
    painter.setBrush(QColor(255, 255, 255, 245 if active else 215))
    painter.drawRoundedRect(QRectF(card_x, card_y, card_w, card_h), card_r, card_r)

    # Card magnetic stripe
    painter.setBrush(QColor(10, 88, 202, 230 if active else 120))
    stripe_h = max(1.5, card_h * 0.22)
    stripe_y = card_y + card_h * 0.16
    painter.drawRect(QRectF(card_x, stripe_y, card_w, stripe_h))

    # Smart Card Chip
    chip_w = max(2.5, card_w * 0.24)
    chip_h = max(2.0, card_h * 0.32)
    chip_x = card_x + card_w * 0.12
    chip_y = card_y + card_h * 0.52
    chip_r = max(0.6, s * 0.02)

    chip_grad = QLinearGradient(chip_x, chip_y, chip_x + chip_w, chip_y + chip_h)
    if active:
        chip_grad.setColorAt(0.0, QColor("#FBBF24"))
        chip_grad.setColorAt(1.0, QColor("#D97706"))
    else:
        chip_grad.setColorAt(0.0, QColor("#CBD5E1"))
        chip_grad.setColorAt(1.0, QColor("#94A3B8"))

    painter.setBrush(QBrush(chip_grad))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(QRectF(chip_x, chip_y, chip_w, chip_h), chip_r, chip_r)

    # Contactless arcs / embossed lines
    line_pen = QPen(QColor(10, 88, 202, 160 if active else 90))
    line_pen.setWidthF(max(1.0, s * 0.035))
    line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(line_pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    c_line_y = chip_y + chip_h * 0.4
    line_start_x = chip_x + chip_w + s * 0.04
    line_end_x = card_x + card_w - s * 0.1
    if line_end_x > line_start_x:
        painter.drawLine(QPointF(line_start_x, c_line_y), QPointF(line_end_x, c_line_y))
        painter.drawLine(
            QPointF(line_start_x, c_line_y + chip_h * 0.35),
            QPointF(line_start_x + (line_end_x - line_start_x) * 0.65, c_line_y + chip_h * 0.35),
        )

    # Status indicator badge (e.g. for tray icon)
    if show_status_dot:
        dot_r = max(2.5, s * 0.14)
        dot_cx = s - pad - dot_r
        dot_cy = s - pad - dot_r

        # Dot outer white border
        painter.setBrush(QColor("#FFFFFF"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(dot_cx, dot_cy), dot_r + max(1.0, s * 0.03), dot_r + max(1.0, s * 0.03))

        # Dot fill
        dot_color = QColor(COLOR_SUCCESS if active else COLOR_WARNING)
        painter.setBrush(dot_color)
        painter.drawEllipse(QPointF(dot_cx, dot_cy), dot_r, dot_r)


# =========================================================================
# 2. Individual Tray Menu & Dialog Vector Icons (16px, 20px, 24px)
# =========================================================================


def _draw_icon_account(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_PRIMARY))
    p.setBrush(color)
    p.setPen(Qt.PenStyle.NoPen)

    # Head
    hr = s * 0.18
    hcx = s * 0.5
    hcy = s * 0.32
    p.drawEllipse(QPointF(hcx, hcy), hr, hr)

    # Shoulders / Torso
    path = QPainterPath()
    bx = s * 0.18
    bw = s * 0.64
    by = s * 0.60
    bh = s * 0.32
    path.moveTo(bx, by + bh)
    path.lineTo(bx, by + bh * 0.4)
    path.quadTo(bx, by, hcx, by)
    path.quadTo(bx + bw, by, bx + bw, by + bh * 0.4)
    path.lineTo(bx + bw, by + bh)
    path.closeSubpath()
    p.drawPath(path)


def _draw_icon_user_badge(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_SLATE))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Badge card outline
    pad = s * 0.18
    p.drawRoundedRect(QRectF(pad, pad + s * 0.05, s - 2 * pad, s - 2 * pad - s * 0.05), s * 0.08, s * 0.08)

    # Top lanyard hole clip
    clip_w = s * 0.22
    p.drawRoundedRect(QRectF((s - clip_w) / 2.0, pad * 0.6, clip_w, s * 0.08), 1.0, 1.0)

    # Mini avatar inside badge
    p.setBrush(color)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(s * 0.5, s * 0.44), s * 0.10, s * 0.10)
    p.drawRoundedRect(QRectF(s * 0.35, s * 0.62, s * 0.30, s * 0.12), 1.5, 1.5)


def _draw_icon_switch_account(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_PRIMARY_LIGHT))
    pen = QPen(color, max(1.3, s * 0.085))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Top arrow (pointing right)
    y1 = s * 0.36
    p.drawLine(QPointF(s * 0.20, y1), QPointF(s * 0.76, y1))
    p.drawLine(QPointF(s * 0.58, y1 - s * 0.14), QPointF(s * 0.78, y1))
    p.drawLine(QPointF(s * 0.58, y1 + s * 0.14), QPointF(s * 0.78, y1))

    # Bottom arrow (pointing left)
    y2 = s * 0.64
    p.drawLine(QPointF(s * 0.80, y2), QPointF(s * 0.24, y2))
    p.drawLine(QPointF(s * 0.42, y2 - s * 0.14), QPointF(s * 0.22, y2))
    p.drawLine(QPointF(s * 0.42, y2 + s * 0.14), QPointF(s * 0.22, y2))


def _draw_icon_history(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_PRIMARY))
    pen = QPen(color, max(1.3, s * 0.085))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Clock dial
    pad = s * 0.15
    p.drawEllipse(QRectF(pad, pad, s - 2 * pad, s - 2 * pad))

    # Clock hands (at 10:10 or 3:00)
    cx = s * 0.5
    cy = s * 0.5
    p.drawLine(QPointF(cx, cy), QPointF(cx, cy - s * 0.22))
    p.drawLine(QPointF(cx, cy), QPointF(cx + s * 0.18, cy))


def _draw_icon_card_item(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_SLATE_LIGHT))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Card outline
    x = s * 0.14
    y = s * 0.24
    w = s * 0.72
    h = s * 0.52
    r = s * 0.08
    p.drawRoundedRect(QRectF(x, y, w, h), r, r)

    # Stripe
    p.setBrush(color)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(QRectF(x, y + h * 0.22, w, h * 0.22))

    # Embossed chip dot
    p.drawRoundedRect(QRectF(x + w * 0.15, y + h * 0.60, w * 0.20, h * 0.22), 1.0, 1.0)


def _draw_icon_empty(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_MUTED))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Box outline with downward fold
    p.drawRoundedRect(QRectF(s * 0.16, s * 0.25, s * 0.68, s * 0.55), s * 0.08, s * 0.08)
    p.drawLine(QPointF(s * 0.16, s * 0.56), QPointF(s * 0.38, s * 0.56))
    p.drawLine(QPointF(s * 0.38, s * 0.56), QPointF(s * 0.44, s * 0.68))
    p.drawLine(QPointF(s * 0.44, s * 0.68), QPointF(s * 0.56, s * 0.68))
    p.drawLine(QPointF(s * 0.56, s * 0.68), QPointF(s * 0.62, s * 0.56))
    p.drawLine(QPointF(s * 0.62, s * 0.56), QPointF(s * 0.84, s * 0.56))


def _draw_icon_main_panel(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_PRIMARY))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Window frame
    x = s * 0.14
    y = s * 0.16
    w = s * 0.72
    h = s * 0.68
    p.drawRoundedRect(QRectF(x, y, w, h), s * 0.10, s * 0.10)

    # Window titlebar line
    p.drawLine(QPointF(x, y + h * 0.28), QPointF(x + w, y + h * 0.28))

    # Control dots
    p.setBrush(color)
    p.setPen(Qt.PenStyle.NoPen)
    dot_r = max(1.0, s * 0.035)
    p.drawEllipse(QPointF(x + w * 0.18, y + h * 0.14), dot_r, dot_r)
    p.drawEllipse(QPointF(x + w * 0.32, y + h * 0.14), dot_r, dot_r)


def _draw_icon_panels(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", "#6366F1"))
    p.setBrush(color)
    p.setPen(Qt.PenStyle.NoPen)

    # 4 squares in 2x2 grid
    gap = s * 0.08
    bw = s * 0.30
    x1 = s * 0.16
    x2 = x1 + bw + gap
    y1 = s * 0.16
    y2 = y1 + bw + gap
    r = s * 0.06

    p.drawRoundedRect(QRectF(x1, y1, bw, bw), r, r)
    p.drawRoundedRect(QRectF(x2, y1, bw, bw), r, r)
    p.drawRoundedRect(QRectF(x1, y2, bw, bw), r, r)
    p.drawRoundedRect(QRectF(x2, y2, bw, bw), r, r)


def _draw_icon_bin_search(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_PRIMARY))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Card outline (smaller to leave room for glass)
    p.drawRoundedRect(QRectF(s * 0.12, s * 0.16, s * 0.60, s * 0.45), s * 0.06, s * 0.06)
    p.drawLine(QPointF(s * 0.12, s * 0.30), QPointF(s * 0.72, s * 0.30))

    # Magnifying glass in bottom right
    gcx = s * 0.64
    gcy = s * 0.64
    gr = s * 0.18
    p.setBrush(QColor("#FFFFFF"))
    p.drawEllipse(QPointF(gcx, gcy), gr, gr)
    p.drawLine(
        QPointF(gcx + gr * 0.70, gcy + gr * 0.70),
        QPointF(s * 0.88, s * 0.88),
    )


def _draw_icon_monitor(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", "#0D9488"))
    pen = QPen(color, max(1.3, s * 0.085))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Central transmitter dot
    p.setBrush(color)
    p.drawEllipse(QPointF(s * 0.30, s * 0.70), s * 0.09, s * 0.09)

    # Radar wave 1
    p.setBrush(Qt.BrushStyle.NoBrush)
    rect1 = QRectF(s * 0.10, s * 0.50, s * 0.40, s * 0.40)
    p.drawArc(rect1, 0, 90 * 16)

    # Radar wave 2
    rect2 = QRectF(s * -0.05, s * 0.35, s * 0.70, s * 0.70)
    p.drawArc(rect2, 0, 90 * 16)

    # Radar wave 3
    rect3 = QRectF(s * -0.20, s * 0.20, s * 1.00, s * 1.00)
    p.drawArc(rect3, 0, 90 * 16)


def _draw_icon_monitor_toggle(p: QPainter, s: int, opt: dict) -> None:
    is_on = opt.get("is_on", True)
    color = QColor(COLOR_SUCCESS if is_on else COLOR_WARNING)
    p.setBrush(color)
    p.setPen(Qt.PenStyle.NoPen)

    # Background circle
    pad = s * 0.12
    p.drawEllipse(QRectF(pad, pad, s - 2 * pad, s - 2 * pad))

    # Symbol inside
    p.setBrush(QColor("#FFFFFF"))
    p.setPen(Qt.PenStyle.NoPen)
    if is_on:
        # Checkmark
        pen = QPen(QColor("#FFFFFF"), max(1.5, s * 0.10))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(QPointF(s * 0.32, s * 0.52), QPointF(s * 0.46, s * 0.66))
        p.drawLine(QPointF(s * 0.46, s * 0.66), QPointF(s * 0.70, s * 0.36))
    else:
        # Pause bars
        bw = max(1.8, s * 0.10)
        bh = s * 0.34
        by = (s - bh) / 2.0
        p.drawRoundedRect(QRectF(s * 0.36, by, bw, bh), 1.0, 1.0)
        p.drawRoundedRect(QRectF(s * 0.54, by, bw, bh), 1.0, 1.0)


def _draw_icon_hotkey(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", "#4F46E5"))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Keyboard body
    p.drawRoundedRect(QRectF(s * 0.12, s * 0.22, s * 0.76, s * 0.56), s * 0.10, s * 0.10)

    # Keys inside
    p.setBrush(color)
    p.setPen(Qt.PenStyle.NoPen)
    kw = s * 0.09
    kh = s * 0.08
    for row in range(2):
        for col in range(4):
            kx = s * 0.22 + col * (s * 0.15)
            ky = s * 0.33 + row * (s * 0.14)
            p.drawRoundedRect(QRectF(kx, ky, kw, kh), 0.8, 0.8)

    # Spacebar
    p.drawRoundedRect(QRectF(s * 0.30, s * 0.62, s * 0.40, kh), 0.8, 0.8)


def _draw_icon_terminal(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_PRIMARY))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Terminal window
    p.drawRoundedRect(QRectF(s * 0.12, s * 0.18, s * 0.76, s * 0.64), s * 0.10, s * 0.10)

    # Prompt >
    p.drawLine(QPointF(s * 0.25, s * 0.40), QPointF(s * 0.40, s * 0.50))
    p.drawLine(QPointF(s * 0.40, s * 0.50), QPointF(s * 0.25, s * 0.60))

    # Cursor _
    p.drawLine(QPointF(s * 0.48, s * 0.60), QPointF(s * 0.68, s * 0.60))


def _draw_icon_cloud_update(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_ACCENT))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Cloud outline
    path = QPainterPath()
    path.moveTo(s * 0.25, s * 0.58)
    path.arcTo(QRectF(s * 0.12, s * 0.44, s * 0.26, s * 0.26), 220, 180)
    path.arcTo(QRectF(s * 0.28, s * 0.20, s * 0.44, s * 0.44), 160, 180)
    path.arcTo(QRectF(s * 0.62, s * 0.44, s * 0.26, s * 0.26), 90, 180)
    path.lineTo(s * 0.25, s * 0.70)
    p.drawPath(path)

    # Download arrow
    cx = s * 0.50
    p.drawLine(QPointF(cx, s * 0.50), QPointF(cx, s * 0.82))
    p.drawLine(QPointF(cx - s * 0.14, s * 0.68), QPointF(cx, s * 0.82))
    p.drawLine(QPointF(cx + s * 0.14, s * 0.68), QPointF(cx, s * 0.82))


def _draw_icon_check_badge(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_PRIMARY_LIGHT))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Shield outline
    path = QPainterPath()
    path.moveTo(s * 0.50, s * 0.15)
    path.lineTo(s * 0.82, s * 0.26)
    path.lineTo(s * 0.82, s * 0.54)
    path.quadTo(s * 0.82, s * 0.82, s * 0.50, s * 0.88)
    path.quadTo(s * 0.18, s * 0.82, s * 0.18, s * 0.54)
    path.lineTo(s * 0.18, s * 0.26)
    path.closeSubpath()
    p.drawPath(path)

    # Checkmark inside
    p.drawLine(QPointF(s * 0.34, s * 0.50), QPointF(s * 0.46, s * 0.62))
    p.drawLine(QPointF(s * 0.46, s * 0.62), QPointF(s * 0.66, s * 0.38))


def _draw_icon_database(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", "#0D9488"))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    w = s * 0.64
    h_disk = s * 0.22
    x = s * 0.18
    y_top = s * 0.18

    # Top disk ellipse
    p.drawEllipse(QRectF(x, y_top, w, h_disk))

    # Middle layer arc & walls
    y_mid = y_top + s * 0.20
    p.drawArc(QRectF(x, y_mid, w, h_disk), 180 * 16, 180 * 16)

    # Bottom layer arc & walls
    y_bot = y_mid + s * 0.20
    p.drawArc(QRectF(x, y_bot, w, h_disk), 180 * 16, 180 * 16)

    # Side connecting walls
    p.drawLine(QPointF(x, y_top + h_disk / 2.0), QPointF(x, y_bot + h_disk / 2.0))
    p.drawLine(QPointF(x + w, y_top + h_disk / 2.0), QPointF(x + w, y_bot + h_disk / 2.0))


def _draw_icon_refresh(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_ACCENT))
    pen = QPen(color, max(1.3, s * 0.085))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Two circular arcs
    rect = QRectF(s * 0.16, s * 0.16, s * 0.68, s * 0.68)
    p.drawArc(rect, 45 * 16, 120 * 16)
    p.drawArc(rect, 225 * 16, 120 * 16)

    # Arrowhead 1 (top-right)
    p.drawLine(QPointF(s * 0.70, s * 0.20), QPointF(s * 0.82, s * 0.32))
    p.drawLine(QPointF(s * 0.72, s * 0.44), QPointF(s * 0.82, s * 0.32))

    # Arrowhead 2 (bottom-left)
    p.drawLine(QPointF(s * 0.30, s * 0.80), QPointF(s * 0.18, s * 0.68))
    p.drawLine(QPointF(s * 0.28, s * 0.56), QPointF(s * 0.18, s * 0.68))


def _draw_icon_sync_db(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", "#059669"))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Database outline on left
    w = s * 0.48
    h_disk = s * 0.18
    x = s * 0.10
    y_top = s * 0.22
    p.drawEllipse(QRectF(x, y_top, w, h_disk))
    p.drawArc(QRectF(x, y_top + s * 0.22, w, h_disk), 180 * 16, 180 * 16)
    p.drawLine(QPointF(x, y_top + h_disk / 2), QPointF(x, y_top + s * 0.22 + h_disk / 2))
    p.drawLine(QPointF(x + w, y_top + h_disk / 2), QPointF(x + w, y_top + s * 0.22 + h_disk / 2))

    # Sync arrows badge on right
    rect_arc = QRectF(s * 0.48, s * 0.42, s * 0.42, s * 0.42)
    p.drawArc(rect_arc, 30 * 16, 180 * 16)
    p.drawArc(rect_arc, 230 * 16, 160 * 16)
    p.drawLine(QPointF(s * 0.86, s * 0.42), QPointF(s * 0.90, s * 0.54))


def _draw_icon_about(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_SLATE))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Circle
    pad = s * 0.15
    p.drawEllipse(QRectF(pad, pad, s - 2 * pad, s - 2 * pad))

    # Lowercase 'i' dot
    p.setBrush(color)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(s * 0.5, s * 0.35), s * 0.06, s * 0.06)

    # Lowercase 'i' stem
    stem_pen = QPen(color, max(1.5, s * 0.09))
    stem_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(stem_pen)
    p.drawLine(QPointF(s * 0.5, s * 0.48), QPointF(s * 0.5, s * 0.68))


def _draw_icon_version_tag(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_SLATE))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Tag shape
    path = QPainterPath()
    path.moveTo(s * 0.18, s * 0.46)
    path.lineTo(s * 0.46, s * 0.18)
    path.lineTo(s * 0.78, s * 0.18)
    path.lineTo(s * 0.78, s * 0.50)
    path.lineTo(s * 0.50, s * 0.78)
    path.lineTo(s * 0.18, s * 0.46)
    path.closeSubpath()
    p.drawPath(path)

    # Tag hole
    p.setBrush(color)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(s * 0.64, s * 0.32), s * 0.06, s * 0.06)


def _draw_icon_calendar(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_SLATE))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Calendar outline
    p.drawRoundedRect(QRectF(s * 0.15, s * 0.22, s * 0.70, s * 0.62), s * 0.08, s * 0.08)

    # Header bar
    p.drawLine(QPointF(s * 0.15, s * 0.40), QPointF(s * 0.85, s * 0.40))

    # Top rings
    p.drawLine(QPointF(s * 0.32, s * 0.14), QPointF(s * 0.32, s * 0.26))
    p.drawLine(QPointF(s * 0.68, s * 0.14), QPointF(s * 0.68, s * 0.26))

    # Grid dots
    p.setBrush(color)
    p.setPen(Qt.PenStyle.NoPen)
    dot_r = max(0.8, s * 0.035)
    for row in range(2):
        for col in range(3):
            p.drawEllipse(
                QPointF(s * 0.32 + col * (s * 0.18), s * 0.52 + row * (s * 0.16)),
                dot_r,
                dot_r,
            )


def _draw_icon_quit(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_DANGER))
    pen = QPen(color, max(1.4, s * 0.09))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Power standby circle with top opening
    rect = QRectF(s * 0.18, s * 0.18, s * 0.64, s * 0.64)
    p.drawArc(rect, 45 * 16, 270 * 16)

    # Vertical notch at top
    p.drawLine(QPointF(s * 0.50, s * 0.14), QPointF(s * 0.50, s * 0.46))


# =========================================================================
# 3. Eye Visibility Icons (for Password Field)
# =========================================================================


def _draw_icon_eye(p: QPainter, s: int, opt: dict) -> None:
    visible = opt.get("visible", True)
    color = QColor(opt.get("color") or (COLOR_PRIMARY if visible else COLOR_MUTED))
    pen = QPen(color, max(1.3, s * 0.085))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Eye contour (two opposed smooth quadratic curves)
    p1 = QPointF(s * 0.12, s * 0.50)
    p2 = QPointF(s * 0.88, s * 0.50)
    top_ctrl = QPointF(s * 0.50, s * 0.16)
    bot_ctrl = QPointF(s * 0.50, s * 0.84)

    path = QPainterPath()
    path.moveTo(p1)
    path.quadTo(top_ctrl, p2)
    path.quadTo(bot_ctrl, p1)
    p.drawPath(path)

    # Center pupil/iris
    if visible:
        p.setBrush(color)
        p.drawEllipse(QPointF(s * 0.50, s * 0.50), s * 0.14, s * 0.14)
    else:
        # Mini iris
        p.setBrush(color)
        p.drawEllipse(QPointF(s * 0.50, s * 0.50), s * 0.10, s * 0.10)
        # Strike-through diagonal slash
        slash_pen = QPen(QColor(COLOR_DANGER), max(1.5, s * 0.095))
        slash_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(slash_pen)
        p.drawLine(QPointF(s * 0.18, s * 0.18), QPointF(s * 0.82, s * 0.82))


# =========================================================================
# 4. Action & Button Icons (Search, Save, Cancel, Copy, Clear, Login)
# =========================================================================


def _draw_icon_search(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", "#FFFFFF"))
    pen = QPen(color, max(1.4, s * 0.09))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    cx = s * 0.44
    cy = s * 0.44
    r = s * 0.24
    p.drawEllipse(QPointF(cx, cy), r, r)

    handle_start_x = cx + r * 0.707
    handle_start_y = cy + r * 0.707
    p.drawLine(QPointF(handle_start_x, handle_start_y), QPointF(s * 0.84, s * 0.84))


def _draw_icon_check(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", "#FFFFFF"))
    pen = QPen(color, max(1.5, s * 0.11))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    p.drawLine(QPointF(s * 0.22, s * 0.50), QPointF(s * 0.42, s * 0.72))
    p.drawLine(QPointF(s * 0.42, s * 0.72), QPointF(s * 0.80, s * 0.28))


def _draw_icon_close(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_SLATE))
    pen = QPen(color, max(1.4, s * 0.10))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    p.drawLine(QPointF(s * 0.26, s * 0.26), QPointF(s * 0.74, s * 0.74))
    p.drawLine(QPointF(s * 0.74, s * 0.26), QPointF(s * 0.26, s * 0.74))


def _draw_icon_copy(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_PRIMARY))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Back paper
    p.drawRoundedRect(QRectF(s * 0.15, s * 0.15, s * 0.50, s * 0.54), s * 0.06, s * 0.06)

    # Front paper (white fill to occlude back)
    p.setBrush(QColor("#FFFFFF"))
    p.drawRoundedRect(QRectF(s * 0.35, s * 0.31, s * 0.50, s * 0.54), s * 0.06, s * 0.06)


def _draw_icon_trash(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", COLOR_DANGER))
    pen = QPen(color, max(1.2, s * 0.08))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Can body
    path = QPainterPath()
    path.moveTo(s * 0.24, s * 0.34)
    path.lineTo(s * 0.28, s * 0.82)
    path.quadTo(s * 0.28, s * 0.86, s * 0.34, s * 0.86)
    path.lineTo(s * 0.66, s * 0.86)
    path.quadTo(s * 0.72, s * 0.86, s * 0.72, s * 0.82)
    path.lineTo(s * 0.76, s * 0.34)
    p.drawPath(path)

    # Lid line
    p.drawLine(QPointF(s * 0.18, s * 0.34), QPointF(s * 0.82, s * 0.34))

    # Top handle
    p.drawRoundedRect(QRectF(s * 0.40, s * 0.20, s * 0.20, s * 0.14), 1.0, 1.0)

    # Inner vertical slots
    p.drawLine(QPointF(s * 0.42, s * 0.46), QPointF(s * 0.42, s * 0.74))
    p.drawLine(QPointF(s * 0.58, s * 0.46), QPointF(s * 0.58, s * 0.74))


def _draw_icon_login(p: QPainter, s: int, opt: dict) -> None:
    color = QColor(opt.get("color", "#FFFFFF"))
    pen = QPen(color, max(1.4, s * 0.09))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Portal bracket
    path = QPainterPath()
    path.moveTo(s * 0.55, s * 0.20)
    path.lineTo(s * 0.78, s * 0.20)
    path.lineTo(s * 0.78, s * 0.80)
    path.lineTo(s * 0.55, s * 0.80)
    p.drawPath(path)

    # Entering arrow
    p.drawLine(QPointF(s * 0.18, s * 0.50), QPointF(s * 0.60, s * 0.50))
    p.drawLine(QPointF(s * 0.44, s * 0.34), QPointF(s * 0.60, s * 0.50))
    p.drawLine(QPointF(s * 0.44, s * 0.66), QPointF(s * 0.60, s * 0.50))


# =========================================================================
# Registry Mapping & Public APIs
# =========================================================================

_DRAW_DISPATCH: Dict[str, Callable[[QPainter, int, dict], None]] = {
    "account": _draw_icon_account,
    "user_badge": _draw_icon_user_badge,
    "switch_account": _draw_icon_switch_account,
    "history": _draw_icon_history,
    "card_item": _draw_icon_card_item,
    "empty": _draw_icon_empty,
    "main_panel": _draw_icon_main_panel,
    "panels": _draw_icon_panels,
    "bin_search": _draw_icon_bin_search,
    "monitor": _draw_icon_monitor,
    "monitor_toggle": _draw_icon_monitor_toggle,
    "hotkey": _draw_icon_hotkey,
    "terminal": _draw_icon_terminal,
    "debug": _draw_icon_terminal,
    "update": _draw_icon_cloud_update,
    "version_check": _draw_icon_check_badge,
    "database": _draw_icon_database,
    "bin_db": _draw_icon_database,
    "refresh": _draw_icon_refresh,
    "sync_db": _draw_icon_sync_db,
    "about": _draw_icon_about,
    "version_tag": _draw_icon_version_tag,
    "calendar": _draw_icon_calendar,
    "quit": _draw_icon_quit,
    "eye": _draw_icon_eye,
    "search": _draw_icon_search,
    "check": _draw_icon_check,
    "close": _draw_icon_close,
    "copy": _draw_icon_copy,
    "trash": _draw_icon_trash,
    "login": _draw_icon_login,
}


def get_app_icon() -> QIcon:
    """Return the master high-resolution BankBin application icon."""
    key = ("app_badge", True, False)
    if key not in _ICON_CACHE:
        _ICON_CACHE[key] = _render_multi_size_icon(
            _draw_app_badge,
            sizes=(16, 20, 24, 32, 48, 64, 128, 256),
            active=True,
            show_status_dot=False,
        )
    return _ICON_CACHE[key]


def get_tray_icon(active: bool = True) -> QIcon:
    """Return the crisp system tray icon with active/paused indicator."""
    key = ("tray_icon", active, True)
    if key not in _ICON_CACHE:
        _ICON_CACHE[key] = _render_multi_size_icon(
            _draw_app_badge,
            sizes=(16, 20, 24, 32, 48, 64),
            active=active,
            show_status_dot=True,
        )
    return _ICON_CACHE[key]


def get_eye_icon(visible: bool = True, color: str | None = None) -> QIcon:
    """Return password eye toggle icon (open or closed)."""
    key = ("eye", visible, color)
    if key not in _ICON_CACHE:
        _ICON_CACHE[key] = _render_multi_size_icon(
            _draw_icon_eye,
            sizes=(16, 20, 24, 32),
            visible=visible,
            color=color,
        )
    return _ICON_CACHE[key]


def get_icon(name: str, **kwargs) -> QIcon:
    """Return a styled vector QIcon by name with optional parameter overrides."""
    name_clean = name.lower().strip()
    draw_fn = _DRAW_DISPATCH.get(name_clean)
    if draw_fn is None:
        return QIcon()

    kwargs_key = tuple(sorted((k, str(v)) for k, v in kwargs.items()))
    cache_key = (name_clean, kwargs_key)
    if cache_key not in _ICON_CACHE:
        sizes = (16, 20, 24, 32)
        _ICON_CACHE[cache_key] = _render_multi_size_icon(draw_fn, sizes=sizes, **kwargs)
    return _ICON_CACHE[cache_key]
