"""Dashboard: project portfolio overview with file import."""

import flet as ft
from flet_app.api_client import ApiClient, ApiError
from flet_app.state import AppState
from flet_app.components.stat_card import stat_card
from flet_app.components.project_card import project_card
from flet_app.components.file_importer import FileImporter
from flet_app import theme as t


def dashboard_view(page: ft.Page, state: AppState, api: ApiClient):
    projects = []
    all_tasks = {}

    # ── File importer (desktop FilePicker) ──
    def handle_import(file_path: str, file_name: str):
        try:
            proj = api.import_project(file_path, file_name)
            t.snackbar(page, f"Imported: {proj.get('name', 'project')}", t.SUCCESS)
            page.go(f"/project/{proj['id']}")
        except ApiError as err:
            t.snackbar(page, str(err), t.ERROR)

    importer = FileImporter(page, on_import=handle_import)

    # ── Stats row ──
    stats_row = ft.Row(
        [
            stat_card("TOTAL PROJECTS", "0"),
            stat_card("ACTIVE TASKS", "0", t.INFO),
            stat_card("COMPLETED", "0", t.SUCCESS),
            stat_card("BLOCKED", "0", t.ERROR),
        ],
        spacing=t.SP_4,
    )

    # ── Project grid ──
    grid = ft.Column(spacing=t.SP_4)

    # ── New project dialog ──
    project_name_field = t.styled_textfield("Project Name")
    project_desc_field = t.styled_textfield("Description")

    def open_new_project(e):
        project_name_field.value = ""
        project_desc_field.value = ""
        new_project_dialog.open = True
        page.update()

    def close_dialog(e):
        new_project_dialog.open = False
        page.update()

    def create_project(e):
        name = project_name_field.value.strip()
        if not name:
            return
        try:
            proj = api.create_project(name, project_desc_field.value.strip() or "")
            new_project_dialog.open = False
            page.update()
            page.go(f"/project/{proj['id']}")
        except ApiError as err:
            t.snackbar(page, str(err), t.ERROR)

    new_project_dialog = ft.AlertDialog(
        modal=True,
        title=t.heading_3("New Project"),
        content=ft.Column([project_name_field, project_desc_field], spacing=t.SP_4, tight=True, width=360),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            t.accent_button("Create", on_click=create_project),
        ],
    )
    page.overlay.append(new_project_dialog)

    def delete_project(project_id):
        def handler(e):
            try:
                api.delete_project(project_id)
                t.snackbar(page, "Project deleted", t.SUCCESS)
                load_data()
            except ApiError as err:
                t.snackbar(page, str(err), t.ERROR)
        return handler

    def navigate_project(project_id):
        def handler(e):
            page.go(f"/project/{project_id}")
        return handler

    def load_data():
        nonlocal projects, all_tasks
        try:
            projects = api.list_projects()
        except ApiError as err:
            if err.status_code == 401:
                page.go("/login")
                return
            t.snackbar(page, str(err), t.ERROR)
            return

        active_count = 0
        done_count = 0
        blocked_count = 0
        all_tasks.clear()

        for p in projects:
            try:
                tasks = api.list_tasks(p["id"])
                counts = {"completed": 0, "active": 0, "blocked": 0}
                for tk in tasks:
                    if tk["status"] == "completed":
                        counts["completed"] += 1
                        done_count += 1
                    elif tk["status"] == "blocked":
                        counts["blocked"] += 1
                        blocked_count += 1
                    else:
                        counts["active"] += 1
                        active_count += 1
                all_tasks[p["id"]] = counts
            except ApiError:
                all_tasks[p["id"]] = {"completed": 0, "active": 0, "blocked": 0}

        stats_row.controls[0] = stat_card("TOTAL PROJECTS", len(projects))
        stats_row.controls[1] = stat_card("ACTIVE TASKS", active_count, t.INFO)
        stats_row.controls[2] = stat_card("COMPLETED", done_count, t.SUCCESS)
        stats_row.controls[3] = stat_card("BLOCKED", blocked_count, t.ERROR)

        render_grid()
        page.update()

    def render_grid():
        grid.controls.clear()
        if not projects:
            empty_state.visible = True
            grid.visible = False
            return

        empty_state.visible = False
        grid.visible = True
        row_controls = []

        for p in projects:
            counts = all_tasks.get(p["id"], {"completed": 0, "active": 0, "blocked": 0})
            card = project_card(p, counts, on_click=navigate_project(p["id"]), on_delete=delete_project(p["id"]))
            row_controls.append(ft.Container(content=card, expand=True))
            if len(row_controls) == 2:
                grid.controls.append(ft.Row(row_controls, spacing=t.SP_4))
                row_controls = []
        if row_controls:
            grid.controls.append(ft.Row(row_controls, spacing=t.SP_4))

    empty_state = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.FOLDER_OUTLINED, size=48, color=t.TEXT_TERTIARY),
                t.heading_3("No projects yet"),
                t.body_secondary("Create your first project or import from a spreadsheet."),
                ft.Container(height=t.SP_3),
                ft.Row(
                    [
                        t.accent_button("Create a Project", on_click=open_new_project, icon=ft.Icons.ADD),
                        t.outlined_button("Import CSV/XLSX", on_click=lambda e: importer.pick(), icon=ft.Icons.UPLOAD_FILE_OUTLINED),
                    ],
                    spacing=t.SP_3,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=t.SP_2,
        ),
        padding=t.SP_10,
        alignment=ft.Alignment.CENTER,
        visible=False,
    )

    header = ft.Row(
        [
            ft.Column(
                [t.heading_1("Projects"), t.body_secondary("Manage and track your project portfolio")],
                spacing=t.SP_1, expand=True,
            ),
            t.outlined_button("Import CSV/XLSX", on_click=lambda e: importer.pick(), icon=ft.Icons.UPLOAD_FILE_OUTLINED),
            t.accent_button("New Project", on_click=open_new_project, icon=ft.Icons.ADD),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    content = ft.Column(
        [header, ft.Container(height=t.SP_4), stats_row, ft.Container(height=t.SP_6), grid, empty_state],
        scroll=ft.ScrollMode.AUTO, expand=True,
    )

    main_area = ft.Container(content=content, padding=t.SP_8, expand=True, bgcolor=t.BG)

    load_data()

    return ft.Column([main_area], expand=True)
