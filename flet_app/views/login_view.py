"""Sign In / Register screen."""

import flet as ft
from flet_app.api_client import ApiClient, ApiError
from flet_app.state import AppState
from flet_app import theme as t


def login_view(page: ft.Page, state: AppState, api: ApiClient):
    is_register = False

    error_text = ft.Text("", color=t.ERROR, size=13, visible=False, font_family=t.FONT_FAMILY)
    username_field = t.styled_textfield("Username")
    password_field = t.styled_textfield("Password", password=True)
    full_name_field = t.styled_textfield("Full Name")
    name_container = ft.Container(content=full_name_field, visible=False)

    submit_btn = t.accent_button("Sign In", on_click=lambda e: handle_submit(e))
    toggle_text = ft.TextButton(
        content="Don't have an account? Create one",
        on_click=lambda e: toggle_mode(e),
        style=ft.ButtonStyle(color=t.ACCENT),
    )

    def toggle_mode(e):
        nonlocal is_register
        is_register = not is_register
        name_container.visible = is_register
        submit_btn.content = "Create Account" if is_register else "Sign In"
        toggle_text.content = "Already have an account? Sign in" if is_register else "Don't have an account? Create one"
        error_text.visible = False
        page.update()

    def handle_submit(e):
        error_text.visible = False
        username = username_field.value.strip()
        password = password_field.value
        full_name = full_name_field.value.strip()

        if not username or not password:
            error_text.value = "Please fill in all required fields."
            error_text.visible = True
            page.update()
            return

        submit_btn.disabled = True
        page.update()

        try:
            if is_register:
                api.register(username, password, full_name or "")

            api.login(username, password)
            # Fetch user profile into state
            try:
                user = api.get_me()
                state.set_user(user)
            except ApiError:
                pass
            page.go("/dashboard")
        except ApiError as err:
            error_text.value = str(err)
            error_text.visible = True
        finally:
            submit_btn.disabled = False
            page.update()

    password_field.on_submit = lambda e: handle_submit(e)

    logo = ft.Container(
        content=ft.Text("S", size=24, weight=ft.FontWeight.W_700, color=t.TEXT_ON_ACCENT, font_family=t.FONT_FAMILY),
        width=56, height=56, bgcolor=t.ACCENT,
        border_radius=t.RADIUS_LG, alignment=ft.Alignment.CENTER,
    )

    form_card = ft.Container(
        content=ft.Column(
            [
                ft.Column(
                    [logo, ft.Container(height=t.SP_3),
                     t.heading_1("Supersonic"),
                     t.body_secondary("Plan at the speed of thought")],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=t.SP_1,
                ),
                ft.Container(height=t.SP_7),
                error_text,
                name_container,
                username_field,
                password_field,
                ft.Container(height=t.SP_2),
                submit_btn,
                ft.Container(content=toggle_text, alignment=ft.Alignment.CENTER),
            ],
            spacing=t.SP_4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=380,
        ),
        bgcolor=t.SURFACE,
        border=ft.border.all(1, t.CARD_BORDER),
        border_radius=t.RADIUS_XL,
        padding=t.SP_9,
        shadow=ft.BoxShadow(
            spread_radius=0, blur_radius=20,
            color=ft.Colors.with_opacity(0.08, "#000000"),
            offset=ft.Offset(0, 4),
        ),
    )

    return ft.Container(
        content=ft.Column(
            [form_card],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        expand=True,
        bgcolor=t.BG,
        alignment=ft.Alignment.CENTER,
    )
