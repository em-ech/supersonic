"""Reusable project card component."""

import flet as ft
from flet_app import theme as t


def project_card(project: dict, task_counts: dict, on_click=None, on_delete=None):
    done = task_counts.get("completed", 0)
    active = task_counts.get("active", 0)
    blocked = task_counts.get("blocked", 0)
    created = project.get("created_at", "")[:10]

    dots = [
        _stat_dot(t.SUCCESS, f"{done} done"),
        _stat_dot(t.INFO, f"{active} active"),
    ]
    if blocked > 0:
        dots.append(_stat_dot(t.ERROR, f"{blocked} blocked"))

    stats_row = ft.Row(
        dots + [ft.Container(expand=True), t.body_secondary(created, size=12)],
        spacing=t.SP_4,
    )

    card_content = ft.Column(
        [
            ft.Row(
                [
                    ft.Text(
                        project.get("name", ""), size=15, weight=ft.FontWeight.W_600,
                        color=t.TEXT_PRIMARY, font_family=t.FONT_FAMILY,
                        expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE, icon_color=t.TEXT_TERTIARY,
                        icon_size=16, tooltip="Delete project", on_click=on_delete,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Text(
                project.get("description") or "No description",
                size=13, color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY,
                max_lines=2, overflow=ft.TextOverflow.ELLIPSIS,
            ),
            ft.Container(height=t.SP_2),
            ft.Divider(height=1, color=t.DIVIDER),
            stats_row,
        ],
        spacing=t.SP_2,
    )

    return ft.Container(
        content=card_content,
        bgcolor=t.CARD,
        border=ft.border.all(1, t.CARD_BORDER),
        border_radius=t.RADIUS_LG,
        padding=t.SP_5,
        on_click=on_click,
        ink=True,
    )


def _stat_dot(color: str, label: str):
    return ft.Row(
        [
            ft.Container(width=7, height=7, bgcolor=color, border_radius=50),
            ft.Text(label, size=12, color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY),
        ],
        spacing=t.SP_1,
    )
