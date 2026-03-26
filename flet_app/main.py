"""Supersonic — Flet Desktop Application Entry Point"""

import flet as ft

from flet_app.state import AppState
from flet_app.api_client import ApiClient, ApiError
from flet_app.components.nav_rail import nav_rail
from flet_app.views.login_view import login_view
from flet_app.views.dashboard_view import dashboard_view
from flet_app.views.project_view import project_view
from flet_app.views.analytics_view import analytics_view
from flet_app.views.ai_chat_view import ai_chat_view
from flet_app import theme as t


def main(page: ft.Page):
    # ── Page setup ──
    page.title = "Supersonic"
    page.bgcolor = t.BG
    page.padding = 0
    page.spacing = 0
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 900
    page.window.min_height = 600
    page.theme = ft.Theme(color_scheme_seed=t.ACCENT, font_family=t.FONT_FAMILY)
    page.theme_mode = ft.ThemeMode.LIGHT

    # ── Shared state + API client ──
    state = AppState()
    api = ApiClient(state)

    # ── Layout containers ──
    content_area = ft.Container(expand=True)
    rail_container = ft.Container(visible=False)

    def handle_nav_change(e):
        idx = e.control.selected_index
        routes = {0: "/dashboard", 1: "/analytics", 2: "/ai-chat", 3: "/profile"}
        route = routes.get(idx)
        if route:
            page.go(route)

    def handle_signout(e):
        state.clear()
        rail_container.visible = False
        page.go("/login")

    def build_rail(selected_index: int):
        rail_container.content = nav_rail(selected_index, on_change=handle_nav_change, on_signout=handle_signout)
        rail_container.visible = True

    def show_profile():
        try:
            me = state.get_user()
            if not me:
                me = api.get_me()
                state.set_user(me)
            name = me.get("full_name") or me.get("username", "")
            username = me.get("username", "")
            created = (me.get("created_at") or "")[:10]

            content_area.content = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Text(
                            name[0].upper() if name else "?",
                            size=32, weight=ft.FontWeight.W_700, color=t.TEXT_ON_ACCENT, font_family=t.FONT_FAMILY,
                        ),
                        width=80, height=80, bgcolor=t.ACCENT, border_radius=50, alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(height=t.SP_4),
                    t.heading_2(name),
                    t.body_secondary(f"@{username}"),
                    ft.Container(height=t.SP_4),
                    t.card_container(ft.Column([
                        ft.Row([t.label_text("Username"), ft.Container(expand=True), t.body_text(username)]),
                        ft.Divider(height=1, color=t.DIVIDER),
                        ft.Row([t.label_text("Full Name"), ft.Container(expand=True), t.body_text(name or "Not set")]),
                        ft.Divider(height=1, color=t.DIVIDER),
                        ft.Row([t.label_text("Member Since"), ft.Container(expand=True), t.body_text(created)]),
                    ], spacing=t.SP_3)),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=t.SP_1),
                padding=t.SP_8,
                expand=True,
                bgcolor=t.BG,
                alignment=ft.Alignment.TOP_CENTER,
            )
            page.update()
        except ApiError:
            page.go("/login")

    def route_change(e):
        route = page.route

        # Clear overlays between views (keeps FilePicker if added)
        page.overlay.clear()

        if route == "/login" or route == "/":
            rail_container.visible = False
            content_area.content = login_view(page, state, api)
        elif route == "/dashboard":
            if not state.is_authenticated():
                page.go("/login")
                return
            # Try to load user on first authed route
            if not state.get_user():
                try:
                    state.set_user(api.get_me())
                except ApiError:
                    pass
            build_rail(0)
            content_area.content = dashboard_view(page, state, api)
        elif route == "/analytics":
            if not state.is_authenticated():
                page.go("/login")
                return
            build_rail(1)
            content_area.content = analytics_view(page, state, api)
        elif route == "/ai-chat":
            if not state.is_authenticated():
                page.go("/login")
                return
            build_rail(2)
            content_area.content = ai_chat_view(page, state, api)
        elif route == "/profile":
            if not state.is_authenticated():
                page.go("/login")
                return
            build_rail(3)
            show_profile()
            return  # show_profile calls page.update
        elif route.startswith("/project/"):
            if not state.is_authenticated():
                page.go("/login")
                return
            pid = route.split("/project/")[1]
            build_rail(0)  # highlight Dashboard when in project detail
            content_area.content = project_view(page, state, api, pid)
        else:
            page.go("/login")
            return

        page.update()

    page.on_route_change = route_change

    # ── Root layout: NavigationRail | Content ──
    page.add(
        ft.Row(
            [
                rail_container,
                ft.VerticalDivider(width=1, color=t.DIVIDER),
                content_area,
            ],
            expand=True,
            spacing=0,
        )
    )

    # ── Initial route: auto-login if JWT persisted ──
    if state.is_authenticated():
        try:
            me = api.get_me()
            state.set_user(me)
            page.go("/dashboard")
        except ApiError:
            state.clear()
            page.go("/login")
    else:
        page.go("/login")


if __name__ == "__main__":
    ft.run(main)
