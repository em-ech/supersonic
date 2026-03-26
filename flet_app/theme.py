"""Supersonic Design System — Light Theme (Flet 0.82.x desktop)."""

import flet as ft

# ── Colors ──
BG = "#f8f9fa"
SURFACE = "#ffffff"
CARD = "#ffffff"
CARD_BORDER = "#e9ecef"
SIDEBAR = "#f1f3f5"

ACCENT = "#7c3aed"
ACCENT_LIGHT = "#ede9fe"
ACCENT_TEXT = "#5b21b6"

SUCCESS = "#16a34a"
SUCCESS_BG = "#dcfce7"
WARNING = "#d97706"
WARNING_BG = "#fef3c7"
ERROR = "#dc2626"
ERROR_BG = "#fee2e2"
INFO = "#2563eb"
INFO_BG = "#dbeafe"

TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6b7280"
TEXT_TERTIARY = "#9ca3af"
TEXT_ON_ACCENT = "#ffffff"

BORDER = "#e5e7eb"
BORDER_FOCUS = ACCENT
DIVIDER = "#f3f4f6"

# ── Status / Priority ──
STATUS_COLORS = {
    "not_started": "#9ca3af",
    "in_progress": "#2563eb",
    "completed": "#16a34a",
    "blocked": "#dc2626",
}

STATUS_BG = {
    "not_started": "#f3f4f6",
    "in_progress": INFO_BG,
    "completed": SUCCESS_BG,
    "blocked": ERROR_BG,
}

PRIORITY_COLORS = {
    "low": "#9ca3af",
    "medium": "#2563eb",
    "high": "#d97706",
    "critical": "#dc2626",
}

PRIORITY_BG = {
    "low": "#f3f4f6",
    "medium": INFO_BG,
    "high": WARNING_BG,
    "critical": ERROR_BG,
}

# ── Typography ──
FONT_FAMILY = "Inter"


def heading_1(text, color=TEXT_PRIMARY):
    return ft.Text(text, size=28, weight=ft.FontWeight.W_700, color=color, font_family=FONT_FAMILY)


def heading_2(text, color=TEXT_PRIMARY):
    return ft.Text(text, size=20, weight=ft.FontWeight.W_600, color=color, font_family=FONT_FAMILY)


def heading_3(text, color=TEXT_PRIMARY):
    return ft.Text(text, size=16, weight=ft.FontWeight.W_600, color=color, font_family=FONT_FAMILY)


def body_text(text, color=TEXT_PRIMARY, size=14):
    return ft.Text(text, size=size, color=color, font_family=FONT_FAMILY)


def body_secondary(text, size=13):
    return ft.Text(text, size=size, color=TEXT_SECONDARY, font_family=FONT_FAMILY)


def label_text(text, color=TEXT_SECONDARY, size=12):
    return ft.Text(
        text.upper(), size=size, weight=ft.FontWeight.W_600,
        color=color, font_family=FONT_FAMILY,
    )


# ── Spacing ──
SP_1 = 4
SP_2 = 8
SP_3 = 12
SP_4 = 16
SP_5 = 20
SP_6 = 24
SP_7 = 32
SP_8 = 40
SP_9 = 48
SP_10 = 64

# ── Radius ──
RADIUS_SM = 6
RADIUS_MD = 10
RADIUS_LG = 14
RADIUS_XL = 20


# ── Component factories ──

def badge(text, bg_color, text_color):
    return ft.Container(
        content=ft.Text(text, size=11, weight=ft.FontWeight.W_500, color=text_color, font_family=FONT_FAMILY),
        bgcolor=bg_color,
        border_radius=RADIUS_SM,
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
    )


def status_badge(status):
    label = status.replace("_", " ").title()
    return badge(label, STATUS_BG.get(status, "#f3f4f6"), STATUS_COLORS.get(status, TEXT_SECONDARY))


def priority_badge(priority):
    return badge(priority.title(), PRIORITY_BG.get(priority, "#f3f4f6"), PRIORITY_COLORS.get(priority, TEXT_SECONDARY))


def card_container(content, padding_val=SP_6):
    return ft.Container(
        content=content,
        bgcolor=CARD,
        border=ft.border.all(1, CARD_BORDER),
        border_radius=RADIUS_LG,
        padding=padding_val,
    )


def accent_button(text, on_click=None, icon=None):
    return ft.Button(
        content=text,
        icon=icon,
        on_click=on_click,
        bgcolor=ACCENT,
        color=TEXT_ON_ACCENT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=RADIUS_MD),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
        ),
    )


def outlined_button(text, on_click=None, icon=None):
    return ft.OutlinedButton(
        content=text,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=TEXT_PRIMARY,
            shape=ft.RoundedRectangleBorder(radius=RADIUS_MD),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            side=ft.BorderSide(1, BORDER),
        ),
    )


def styled_textfield(label, password=False, value="", on_submit=None, multiline=False, min_lines=1, max_lines=1):
    return ft.TextField(
        label=label,
        value=value,
        password=password,
        can_reveal_password=password,
        multiline=multiline,
        min_lines=min_lines,
        max_lines=max_lines,
        border_color=BORDER,
        focused_border_color=BORDER_FOCUS,
        border_radius=RADIUS_MD,
        text_size=14,
        label_style=ft.TextStyle(size=13, color=TEXT_SECONDARY),
        cursor_color=ACCENT,
        on_submit=on_submit,
    )


def styled_dropdown(label, options, value=None, on_select=None):
    return ft.Dropdown(
        label=label,
        value=value,
        options=[ft.dropdown.Option(o) for o in options],
        on_select=on_select,
        border_color=BORDER,
        focused_border_color=BORDER_FOCUS,
        border_radius=RADIUS_MD,
        text_size=14,
        label_style=ft.TextStyle(size=13, color=TEXT_SECONDARY),
    )


def snackbar(page: ft.Page, message: str, color: str = INFO):
    """Show a brief notification."""
    sb = ft.SnackBar(
        content=ft.Text(message, color=TEXT_ON_ACCENT, font_family=FONT_FAMILY),
        bgcolor=color,
        duration=3000,
    )
    page.overlay.append(sb)
    sb.open = True
    page.update()
