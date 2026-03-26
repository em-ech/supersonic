"""Project detail: tasks, messages, AI assistant."""

import flet as ft
from flet_app.api_client import ApiClient, ApiError
from flet_app.state import AppState
from flet_app.components.task_row import task_row
from flet_app.components.gantt_chart import gantt_chart
from flet_app import theme as t


def project_view(page: ft.Page, state: AppState, api: ApiClient, project_id: str):
    project = {}
    tasks = []
    messages = []
    current_filter = "all"
    editing_task_id = None

    # ── Progress bar ──
    progress_label = ft.Text("0 of 0 tasks completed", size=13, color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY)
    progress_pct = ft.Text("0%", size=13, color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY)
    progress_bar = ft.ProgressBar(value=0, color=t.ACCENT, bgcolor=t.DIVIDER, bar_height=5, border_radius=3)

    # ── Lists ──
    task_list_col = ft.Column(spacing=t.SP_2)
    message_list_col = ft.Column(spacing=t.SP_4)

    # ── AI results ──
    ai_summary_text = ft.Text(
        "Select a focus area to generate a summary.", size=14,
        color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY, selectable=True,
    )
    ai_suggest_text = ft.Text(
        "Enter a prompt or click generate for recommendations.", size=14,
        color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY, selectable=True,
    )
    ai_prompt_field = t.styled_textfield("Ask for scheduling or priority advice...")

    # ── Task form fields ──
    task_title_field = t.styled_textfield("Title")
    task_desc_field = t.styled_textfield("Description")
    task_status_dd = t.styled_dropdown("Status", ["not_started", "in_progress", "completed", "blocked"], "not_started")
    task_priority_dd = t.styled_dropdown("Priority", ["low", "medium", "high", "critical"], "medium")
    task_assignee_field = t.styled_textfield("Assignee")
    task_start_field = t.styled_textfield("Start Date (YYYY-MM-DD)")
    task_end_field = t.styled_textfield("End Date (YYYY-MM-DD)")

    # ── Message form fields ──
    msg_subject_field = t.styled_textfield("Subject")
    msg_sender_field = t.styled_textfield("From")
    msg_body_field = t.styled_textfield("Body", multiline=True, min_lines=3, max_lines=6)

    # ── Edit project fields ──
    edit_name_field = t.styled_textfield("Project Name")
    edit_desc_field = t.styled_textfield("Description")

    # ── Dialogs ──
    def open_task_dialog(e=None, task=None):
        nonlocal editing_task_id
        if task:
            editing_task_id = task["id"]
            task_title_field.value = task.get("title", "")
            task_desc_field.value = task.get("description", "") or ""
            task_status_dd.value = task.get("status", "not_started")
            task_priority_dd.value = task.get("priority", "medium")
            task_assignee_field.value = task.get("assignee", "") or ""
            task_start_field.value = (task.get("start_date") or "")[:10]
            task_end_field.value = (task.get("end_date") or "")[:10]
            task_dialog.title = t.heading_3("Edit Task")
        else:
            editing_task_id = None
            task_title_field.value = ""
            task_desc_field.value = ""
            task_status_dd.value = "not_started"
            task_priority_dd.value = "medium"
            task_assignee_field.value = ""
            task_start_field.value = ""
            task_end_field.value = ""
            task_dialog.title = t.heading_3("New Task")
        task_dialog.open = True
        page.update()

    def save_task(e):
        title = task_title_field.value.strip()
        if not title:
            return
        kwargs = {
            "title": title,
            "description": task_desc_field.value.strip() or None,
            "status": task_status_dd.value,
            "priority": task_priority_dd.value,
            "assignee": task_assignee_field.value.strip() or None,
            "start_date": task_start_field.value.strip() or None,
            "end_date": task_end_field.value.strip() or None,
        }
        try:
            if editing_task_id:
                api.update_task(editing_task_id, **kwargs)
                t.snackbar(page, "Task updated", t.SUCCESS)
            else:
                api.create_task(project_id, **kwargs)
                t.snackbar(page, "Task created", t.SUCCESS)
            task_dialog.open = False
            page.update()
            load_tasks()
        except ApiError as err:
            t.snackbar(page, str(err), t.ERROR)

    def close_task_dialog(e):
        task_dialog.open = False
        page.update()

    task_dialog = ft.AlertDialog(
        modal=True,
        title=t.heading_3("New Task"),
        content=ft.Column(
            [
                task_title_field, task_desc_field,
                ft.Row([task_status_dd, task_priority_dd], spacing=t.SP_4),
                task_assignee_field,
                ft.Row([task_start_field, task_end_field], spacing=t.SP_4),
            ],
            spacing=t.SP_4, tight=True, width=420,
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_task_dialog),
            t.accent_button("Save", on_click=save_task),
        ],
    )
    page.overlay.append(task_dialog)

    def delete_task_handler(task_id):
        def handler(e):
            try:
                api.delete_task(task_id)
                t.snackbar(page, "Task deleted", t.SUCCESS)
                load_tasks()
            except ApiError as err:
                t.snackbar(page, str(err), t.ERROR)
        return handler

    def edit_task_handler(task_data):
        def handler(e):
            open_task_dialog(task=task_data)
        return handler

    # ── Message dialog ──
    def open_message_dialog(e=None):
        msg_subject_field.value = ""
        msg_sender_field.value = ""
        msg_body_field.value = ""
        message_dialog.open = True
        page.update()

    def save_message(e):
        subject = msg_subject_field.value.strip()
        if not subject:
            return
        try:
            api.create_message(
                project_id,
                subject=subject,
                body=msg_body_field.value.strip() or None,
                sender=msg_sender_field.value.strip() or None,
            )
            message_dialog.open = False
            page.update()
            t.snackbar(page, "Message added", t.SUCCESS)
            load_messages()
        except ApiError as err:
            t.snackbar(page, str(err), t.ERROR)

    def close_message_dialog(e):
        message_dialog.open = False
        page.update()

    message_dialog = ft.AlertDialog(
        modal=True,
        title=t.heading_3("New Message"),
        content=ft.Column([msg_subject_field, msg_sender_field, msg_body_field], spacing=t.SP_4, tight=True, width=400),
        actions=[
            ft.TextButton("Cancel", on_click=close_message_dialog),
            t.accent_button("Send", on_click=save_message),
        ],
    )
    page.overlay.append(message_dialog)

    # ── Edit project dialog ──
    def open_edit_project(e):
        edit_name_field.value = project.get("name", "")
        edit_desc_field.value = project.get("description", "") or ""
        edit_dialog.open = True
        page.update()

    def save_project_edit(e):
        try:
            api.update_project(project_id, edit_name_field.value.strip(), edit_desc_field.value.strip() or None)
            edit_dialog.open = False
            page.update()
            t.snackbar(page, "Project updated", t.SUCCESS)
            load_project()
        except ApiError as err:
            t.snackbar(page, str(err), t.ERROR)

    def close_edit_dialog(e):
        edit_dialog.open = False
        page.update()

    def delete_project(e):
        try:
            api.delete_project(project_id)
            t.snackbar(page, "Project deleted", t.SUCCESS)
            page.go("/dashboard")
        except ApiError as err:
            t.snackbar(page, str(err), t.ERROR)

    edit_dialog = ft.AlertDialog(
        modal=True,
        title=t.heading_3("Edit Project"),
        content=ft.Column([edit_name_field, edit_desc_field], spacing=t.SP_4, tight=True, width=400),
        actions=[
            ft.TextButton("Cancel", on_click=close_edit_dialog),
            t.accent_button("Save", on_click=save_project_edit),
        ],
    )
    page.overlay.append(edit_dialog)

    # ── Filter chips ──
    filter_row = ft.Row(spacing=t.SP_2)

    def set_filter(f):
        def handler(e):
            nonlocal current_filter
            current_filter = f
            render_tasks()
            page.update()
        return handler

    def filter_chip(label, value):
        is_active = current_filter == value
        return ft.Container(
            content=ft.Text(
                label, size=13, weight=ft.FontWeight.W_500,
                color=t.ACCENT if is_active else t.TEXT_SECONDARY, font_family=t.FONT_FAMILY,
            ),
            bgcolor=t.ACCENT_LIGHT if is_active else "transparent",
            border=ft.border.all(1, t.ACCENT if is_active else t.BORDER),
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=14, vertical=6),
            on_click=set_filter(value),
            ink=True,
        )

    def rebuild_filters():
        filter_row.controls = [
            filter_chip("All", "all"),
            filter_chip("Not Started", "not_started"),
            filter_chip("In Progress", "in_progress"),
            filter_chip("Completed", "completed"),
            filter_chip("Blocked", "blocked"),
        ]

    # ── AI handlers ──
    def get_summary(focus=None):
        def handler(e):
            ai_summary_text.value = "Generating..."
            page.update()
            try:
                data = api.ai_summary(project_id, focus)
                ai_summary_text.value = data.get("result", "")
                if data.get("disclaimer"):
                    ai_summary_text.value += f"\n\n{data['disclaimer']}"
            except ApiError as err:
                ai_summary_text.value = str(err)
            page.update()
        return handler

    def get_suggestions(e):
        ai_suggest_text.value = "Thinking..."
        page.update()
        try:
            prompt = ai_prompt_field.value.strip() or None
            data = api.ai_suggestions(project_id, prompt)
            ai_suggest_text.value = data.get("result", "")
            if data.get("disclaimer"):
                ai_suggest_text.value += f"\n\n{data['disclaimer']}"
        except ApiError as err:
            ai_suggest_text.value = str(err)
        page.update()

    # ── Data loading ──
    project_title = ft.Text("", size=24, weight=ft.FontWeight.W_700, color=t.TEXT_PRIMARY, font_family=t.FONT_FAMILY)
    project_desc = ft.Text("", size=14, color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY)

    def load_project():
        nonlocal project
        try:
            project = api.get_project(project_id)
            project_title.value = project.get("name", "")
            project_desc.value = project.get("description", "") or ""
        except ApiError as err:
            if err.status_code == 401:
                page.go("/login")
                return
            t.snackbar(page, str(err), t.ERROR)
        page.update()

    def load_tasks():
        nonlocal tasks
        try:
            tasks = api.list_tasks(project_id)
        except ApiError:
            tasks = []
        update_progress()
        render_tasks()
        rebuild_gantt()
        page.update()

    def load_messages():
        nonlocal messages
        try:
            messages = api.list_messages(project_id)
        except ApiError:
            messages = []
        render_messages()
        page.update()

    def update_progress():
        total = len(tasks)
        done = sum(1 for tk in tasks if tk["status"] == "completed")
        pct = round((done / total) * 100) if total > 0 else 0
        progress_label.value = f"{done} of {total} tasks completed"
        progress_pct.value = f"{pct}%"
        progress_bar.value = pct / 100

    def render_tasks():
        rebuild_filters()
        filtered = tasks if current_filter == "all" else [tk for tk in tasks if tk["status"] == current_filter]
        task_list_col.controls.clear()

        if not tasks:
            task_empty.visible = True
            task_list_col.visible = False
            filter_row.visible = False
            return

        filter_row.visible = True
        task_empty.visible = False
        task_list_col.visible = True

        if not filtered:
            task_list_col.controls.append(
                ft.Container(
                    content=t.body_secondary("No tasks match this filter."),
                    padding=t.SP_8, alignment=ft.Alignment.CENTER,
                )
            )
            return

        for tk in filtered:
            task_list_col.controls.append(
                task_row(tk, on_edit=edit_task_handler(tk), on_delete=delete_task_handler(tk["id"]))
            )

    def render_messages():
        message_list_col.controls.clear()
        if not messages:
            message_empty.visible = True
            message_list_col.visible = False
            return

        message_empty.visible = False
        message_list_col.visible = True

        for m in messages:
            date_str = (m.get("date") or "")[:16].replace("T", " ")
            message_list_col.controls.append(
                t.card_container(
                    ft.Column([
                        ft.Row([
                            ft.Text(m.get("subject", ""), size=15, weight=ft.FontWeight.W_600, color=t.TEXT_PRIMARY, font_family=t.FONT_FAMILY, expand=True),
                            ft.Text(date_str, size=12, color=t.TEXT_TERTIARY, font_family=t.FONT_FAMILY),
                        ]),
                        ft.Text(f"From: {m.get('sender', 'Unknown')}", size=13, color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY) if m.get("sender") else ft.Container(),
                        ft.Text(m.get("body", ""), size=14, color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY),
                    ], spacing=t.SP_2)
                )
            )

    task_empty = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.CHECK_BOX_OUTLINED, size=40, color=t.TEXT_TERTIARY),
                t.heading_3("No tasks yet"),
                t.body_secondary("Break your project down into actionable tasks."),
                ft.Container(height=t.SP_2),
                t.accent_button("Add First Task", on_click=lambda e: open_task_dialog(), icon=ft.Icons.ADD),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=t.SP_2,
        ),
        padding=t.SP_10, alignment=ft.Alignment.CENTER, visible=False,
    )

    message_empty = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, size=40, color=t.TEXT_TERTIARY),
                t.heading_3("No messages"),
                t.body_secondary("Attach notes and emails to keep context in one place."),
                ft.Container(height=t.SP_2),
                t.accent_button("Add a Message", on_click=open_message_dialog, icon=ft.Icons.ADD),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=t.SP_2,
        ),
        padding=t.SP_10, alignment=ft.Alignment.CENTER, visible=False,
    )

    # ── Gantt container (rebuilt on each load_tasks) ──
    gantt_container = ft.Container(expand=True)

    def rebuild_gantt():
        gantt_container.content = gantt_chart(tasks)

    # ── Tabs ──
    tasks_tab = ft.Column([
        ft.Row([
            filter_row, ft.Container(expand=True),
            t.accent_button("Add Task", on_click=lambda e: open_task_dialog(), icon=ft.Icons.ADD),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        task_list_col,
        task_empty,
    ], spacing=t.SP_4)

    messages_tab = ft.Column([
        ft.Row([ft.Container(expand=True), t.accent_button("New Message", on_click=open_message_dialog, icon=ft.Icons.ADD)]),
        message_list_col,
        message_empty,
    ], spacing=t.SP_4)

    ai_tab = ft.Row([
        ft.Container(
            content=t.card_container(ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.SUMMARIZE_OUTLINED, size=18, color=t.ACCENT),
                        width=36, height=36, bgcolor=t.ACCENT_LIGHT, border_radius=t.RADIUS_MD, alignment=ft.Alignment.CENTER,
                    ),
                    t.heading_3("Project Summary"),
                ], spacing=t.SP_3),
                ft.Row([
                    t.outlined_button("Overview", on_click=get_summary()),
                    t.outlined_button("Risks", on_click=get_summary("risks")),
                    t.outlined_button("Timeline", on_click=get_summary("timeline")),
                    t.outlined_button("Workload", on_click=get_summary("workload")),
                ], spacing=t.SP_2, wrap=True),
                ai_summary_text,
            ], spacing=t.SP_4)),
            expand=True,
        ),
        ft.Container(
            content=t.card_container(ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.AUTO_AWESOME_OUTLINED, size=18, color=t.ACCENT),
                        width=36, height=36, bgcolor=t.ACCENT_LIGHT, border_radius=t.RADIUS_MD, alignment=ft.Alignment.CENTER,
                    ),
                    t.heading_3("Suggestions"),
                ], spacing=t.SP_3),
                ai_prompt_field,
                t.outlined_button("Generate Suggestions", on_click=get_suggestions),
                ai_suggest_text,
            ], spacing=t.SP_4)),
            expand=True,
        ),
    ], spacing=t.SP_6)

    tab_bar = ft.TabBar(
        tabs=[
            ft.Tab(label="Tasks"),
            ft.Tab(label="Gantt"),
            ft.Tab(label="Messages"),
            ft.Tab(label="AI Assistant"),
        ],
        label_color=t.ACCENT,
        unselected_label_color=t.TEXT_SECONDARY,
        indicator_color=t.ACCENT,
    )

    tab_bar_view = ft.TabBarView(
        controls=[
            ft.Container(content=tasks_tab, padding=ft.padding.only(top=t.SP_4)),
            ft.Container(content=gantt_container, padding=ft.padding.only(top=t.SP_4)),
            ft.Container(content=messages_tab, padding=ft.padding.only(top=t.SP_4)),
            ft.Container(content=ai_tab, padding=ft.padding.only(top=t.SP_4)),
        ],
        expand=True,
    )

    tabs = ft.Tabs(
        content=ft.Column([tab_bar, tab_bar_view], expand=True, spacing=0),
        length=4,
        selected_index=0,
        animation_duration=200,
        expand=True,
    )

    # ── Header ──
    breadcrumb = ft.Row([
        ft.TextButton("Projects", on_click=lambda e: page.go("/dashboard"), style=ft.ButtonStyle(color=t.TEXT_TERTIARY)),
        ft.Text("/", size=13, color=t.TEXT_TERTIARY),
        ft.Text("", size=13, color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY),
    ], spacing=t.SP_1)

    header = ft.Column([
        breadcrumb,
        ft.Row([
            ft.Column([project_title, project_desc], spacing=t.SP_1, expand=True),
            t.outlined_button("Edit", on_click=open_edit_project, icon=ft.Icons.EDIT_OUTLINED),
            ft.OutlinedButton(
                content="Delete", icon=ft.Icons.DELETE_OUTLINE,
                on_click=delete_project,
                style=ft.ButtonStyle(
                    color=t.ERROR,
                    shape=ft.RoundedRectangleBorder(radius=t.RADIUS_MD),
                    side=ft.BorderSide(1, t.ERROR),
                ),
            ),
        ]),
        ft.Container(height=t.SP_2),
        ft.Row([progress_label, ft.Container(expand=True), progress_pct]),
        progress_bar,
    ], spacing=t.SP_2)

    content = ft.Column([header, ft.Container(height=t.SP_4), tabs], expand=True)
    main_area = ft.Container(content=content, padding=t.SP_8, expand=True, bgcolor=t.BG)

    # Load data
    load_project()
    load_tasks()
    load_messages()

    # Update breadcrumb with project name
    if len(breadcrumb.controls) >= 3:
        breadcrumb.controls[2] = ft.Text(
            project.get("name", ""), size=13, color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY,
        )

    return ft.Column([main_area], expand=True)
