"""Reusable task row component."""

import flet as ft
from flet_app import theme as t


def task_row(task: dict, on_edit=None, on_delete=None):
    status = task.get("status", "not_started")
    priority = task.get("priority", "medium")
    assignee = task.get("assignee", "")
    end_date = (task.get("end_date") or "")[:10]

    initials = ""
    if assignee:
        parts = assignee.split()
        initials = "".join(p[0].upper() for p in parts[:2])

    assignee_chip = ft.Row(
        [
            ft.Container(
                content=ft.Text(initials, size=10, weight=ft.FontWeight.W_600, color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY),
                width=24, height=24, bgcolor=t.DIVIDER, border_radius=50,
                alignment=ft.Alignment.CENTER,
            ),
            ft.Text(assignee, size=13, color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY),
        ],
        spacing=t.SP_1,
        visible=bool(assignee),
    )

    return ft.Container(
        content=ft.Row(
            [
                ft.Container(width=9, height=9, bgcolor=t.STATUS_COLORS.get(status, t.TEXT_TERTIARY), border_radius=50),
                ft.Column(
                    [
                        ft.Text(
                            task.get("title", ""), size=14, weight=ft.FontWeight.W_500,
                            color=t.TEXT_PRIMARY, font_family=t.FONT_FAMILY,
                            expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Row([t.status_badge(status), t.priority_badge(priority)], spacing=t.SP_2),
                    ],
                    spacing=t.SP_1,
                    expand=True,
                ),
                assignee_chip,
                ft.Text(end_date, size=12, color=t.TEXT_TERTIARY, font_family=t.FONT_FAMILY, visible=bool(end_date)),
                ft.Row(
                    [
                        ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_size=16, icon_color=t.TEXT_TERTIARY, tooltip="Edit", on_click=on_edit),
                        ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_size=16, icon_color=t.TEXT_TERTIARY, tooltip="Delete", on_click=on_delete),
                    ],
                    spacing=0,
                ),
            ],
            spacing=t.SP_4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=t.CARD,
        border=ft.border.all(1, t.CARD_BORDER),
        border_radius=t.RADIUS_MD,
        padding=ft.padding.symmetric(horizontal=t.SP_5, vertical=t.SP_3),
    )
