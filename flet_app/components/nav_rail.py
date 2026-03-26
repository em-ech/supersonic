"""NavigationRail wrapper for desktop layout."""

import flet as ft
from flet_app import theme as t


def nav_rail(selected_index: int, on_change, on_signout):
    """Desktop-native NavigationRail with app destinations."""
    return ft.NavigationRail(
        selected_index=selected_index,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        min_extended_width=200,
        bgcolor=t.SIDEBAR,
        indicator_color=t.ACCENT_LIGHT,
        on_change=on_change,
        leading=ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.ROCKET_LAUNCH_ROUNDED, color=t.ACCENT, size=28),
                    ft.Text("Supersonic", size=11, weight=ft.FontWeight.W_700, color=t.ACCENT, font_family=t.FONT_FAMILY),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            padding=ft.padding.only(top=t.SP_4, bottom=t.SP_6),
        ),
        trailing=ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.LOGOUT_ROUNDED,
                icon_color=t.TEXT_TERTIARY,
                icon_size=20,
                tooltip="Sign out",
                on_click=on_signout,
            ),
            padding=ft.padding.only(bottom=t.SP_4),
        ),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Dashboard",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.ANALYTICS_OUTLINED,
                selected_icon=ft.Icons.ANALYTICS,
                label="Analytics",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CHAT_OUTLINED,
                selected_icon=ft.Icons.CHAT,
                label="AI Chat",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PERSON_OUTLINED,
                selected_icon=ft.Icons.PERSON,
                label="Profile",
            ),
        ],
    )
