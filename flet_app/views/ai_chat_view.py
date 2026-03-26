"""AI Chat: conversational interface for project intelligence."""

import flet as ft
from flet_app.api_client import ApiClient, ApiError
from flet_app.state import AppState
from flet_app.components.chat_bubble import chat_bubble
from flet_app import theme as t


def ai_chat_view(page: ft.Page, state: AppState, api: ApiClient):
    projects = []
    selected_project_id = None
    messages_list = []

    chat_column = ft.Column(spacing=t.SP_4, scroll=ft.ScrollMode.AUTO, expand=True)
    input_field = ft.TextField(
        hint_text="Ask about your project...",
        border_color=t.BORDER,
        focused_border_color=t.ACCENT,
        border_radius=t.RADIUS_MD,
        text_size=14,
        expand=True,
        on_submit=lambda e: send_message(e),
    )

    # ── Quick action chips ──
    def quick_action(label, focus=None):
        def handler(e):
            nonlocal selected_project_id
            if not selected_project_id:
                add_bot_message("Please select a project first.")
                return
            input_field.value = ""
            add_user_message(label)
            generate_response(focus=focus)
        return handler

    quick_actions = ft.Row([
        _chip("Overview", quick_action("Give me an overview")),
        _chip("Risks", quick_action("Analyze risks", "risks")),
        _chip("Timeline", quick_action("Review timeline", "timeline")),
        _chip("Workload", quick_action("Check workload", "workload")),
    ], spacing=t.SP_2, wrap=True)

    # ── Project selector ──
    project_dropdown = ft.Dropdown(
        label="Select a project",
        options=[],
        border_color=t.BORDER,
        focused_border_color=t.ACCENT,
        border_radius=t.RADIUS_MD,
        text_size=14,
        width=350,
        on_select=lambda e: on_project_select(e),
    )

    def on_project_select(e):
        nonlocal selected_project_id
        selected_project_id = project_dropdown.value
        proj_name = next((p["name"] for p in projects if p["id"] == project_dropdown.value), "this project")
        chat_column.controls.clear()
        messages_list.clear()
        add_bot_message(f"Ready to analyze {proj_name}. Ask me anything about the project, or use the quick actions below.")
        page.update()

    def add_user_message(text):
        messages_list.append(("user", text))
        chat_column.controls.append(chat_bubble(text, is_user=True))
        page.update()

    def add_bot_message(text):
        messages_list.append(("bot", text))
        chat_column.controls.append(chat_bubble(text, is_user=False))
        page.update()

    def send_message(e):
        text = input_field.value.strip()
        if not text:
            return
        if not selected_project_id:
            add_bot_message("Please select a project first using the dropdown above.")
            return
        input_field.value = ""
        add_user_message(text)
        generate_response(prompt=text)

    def generate_response(focus=None, prompt=None):
        typing = _typing_indicator()
        chat_column.controls.append(typing)
        page.update()

        try:
            pid = selected_project_id
            if focus:
                data = api.ai_summary(pid, focus)
            elif prompt:
                data = api.ai_chat(pid, prompt)
            else:
                data = api.ai_summary(pid)

            result = data.get("result", "No response generated.")
            disclaimer = data.get("disclaimer", "")
            chat_column.controls.remove(typing)
            response = result
            if disclaimer:
                response += f"\n\n{disclaimer}"
            add_bot_message(response)
        except ApiError as err:
            chat_column.controls.remove(typing)
            add_bot_message(f"Something went wrong: {err}")

    def load_data():
        nonlocal projects
        try:
            projects = api.list_projects()
            project_dropdown.options = [
                ft.dropdown.Option(key=p["id"], text=p["name"]) for p in projects
            ]
        except ApiError as err:
            if err.status_code == 401:
                page.go("/login")
                return

        chat_column.controls.clear()
        add_bot_message(
            "Welcome to the Supersonic AI Assistant. "
            "Select a project above to get started, then ask me about risks, timelines, workload, or anything else."
        )
        page.update()

    # ── Layout ──
    send_btn = ft.IconButton(
        icon=ft.Icons.SEND, icon_color=t.TEXT_ON_ACCENT,
        bgcolor=t.ACCENT, on_click=send_message, icon_size=20,
    )

    input_row = ft.Row(
        [input_field, send_btn],
        spacing=t.SP_2,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    chat_area = t.card_container(
        ft.Column([
            chat_column,
            ft.Divider(color=t.DIVIDER),
            ft.Container(height=t.SP_2),
            quick_actions,
            ft.Container(height=t.SP_2),
            input_row,
        ], spacing=0, expand=True),
        padding_val=t.SP_5,
    )

    content = ft.Column([
        ft.Row([
            t.heading_1("AI Assistant"),
            ft.Container(expand=True),
            project_dropdown,
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Container(height=t.SP_4),
        ft.Container(content=chat_area, expand=True),
    ], expand=True)

    main_area = ft.Container(content=content, padding=t.SP_8, expand=True, bgcolor=t.BG)

    load_data()

    return ft.Column([main_area], expand=True)


def _typing_indicator():
    return ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Icon(ft.Icons.AUTO_AWESOME, size=16, color=t.ACCENT),
                width=32, height=32, bgcolor=t.ACCENT_LIGHT, border_radius=50, alignment=ft.Alignment.CENTER,
            ),
            ft.Container(
                content=ft.Row([
                    ft.ProgressRing(width=14, height=14, stroke_width=2, color=t.ACCENT),
                    ft.Text("Thinking...", size=13, color=t.TEXT_TERTIARY, font_family=t.FONT_FAMILY, italic=True),
                ], spacing=t.SP_2),
                bgcolor=t.SURFACE, border=ft.border.all(1, t.CARD_BORDER),
                border_radius=t.RADIUS_LG, padding=t.SP_4,
            ),
        ], spacing=t.SP_3),
    )


def _chip(label, on_click):
    return ft.Container(
        content=ft.Text(label, size=12, weight=ft.FontWeight.W_500, color=t.ACCENT, font_family=t.FONT_FAMILY),
        bgcolor=t.ACCENT_LIGHT, border=ft.border.all(1, t.ACCENT),
        border_radius=20, padding=ft.padding.symmetric(horizontal=14, vertical=6),
        on_click=on_click, ink=True,
    )
