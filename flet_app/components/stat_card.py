"""Reusable stat card component."""

import flet as ft
from flet_app import theme as t


def stat_card(label: str, value, color: str = t.TEXT_PRIMARY):
    return ft.Container(
        content=ft.Column(
            [
                t.label_text(label),
                ft.Text(
                    str(value), size=32, weight=ft.FontWeight.W_700,
                    color=color, font_family=t.FONT_FAMILY,
                ),
            ],
            spacing=t.SP_1,
        ),
        bgcolor=t.CARD,
        border=ft.border.all(1, t.CARD_BORDER),
        border_radius=t.RADIUS_LG,
        padding=ft.padding.symmetric(horizontal=t.SP_6, vertical=t.SP_5),
        expand=True,
    )
