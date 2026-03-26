"""Chat message bubble for AI chat view."""

import flet as ft
from flet_app import theme as t


def chat_bubble(text: str, is_user: bool = True):
    """Render a chat message bubble."""
    if is_user:
        bg = t.ACCENT
        text_color = t.TEXT_ON_ACCENT
        align = ft.MainAxisAlignment.END
    else:
        bg = t.SURFACE
        text_color = t.TEXT_PRIMARY
        align = ft.MainAxisAlignment.START

    bubble = ft.Container(
        content=ft.Text(
            text, size=14, color=text_color, font_family=t.FONT_FAMILY,
            selectable=True,
        ),
        bgcolor=bg,
        border=None if is_user else ft.border.all(1, t.CARD_BORDER),
        border_radius=ft.border_radius.only(
            top_left=t.RADIUS_LG,
            top_right=t.RADIUS_LG,
            bottom_left=t.RADIUS_LG if is_user else t.RADIUS_SM,
            bottom_right=t.RADIUS_SM if is_user else t.RADIUS_LG,
        ),
        padding=ft.padding.symmetric(horizontal=t.SP_4, vertical=t.SP_3),
        width=480,
    )

    return ft.Row([bubble], alignment=align)
