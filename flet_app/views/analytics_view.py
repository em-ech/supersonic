"""Analytics dashboard with data visualization and risk analysis."""

import flet as ft
from flet_app.api_client import ApiClient, ApiError
from flet_app.state import AppState
from flet_app import theme as t


def analytics_view(page: ft.Page, state: AppState, api: ApiClient):
    projects = []
    all_tasks = {}
    risk_text = ft.Text("", size=14, color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY, selectable=True)
    risk_loading = ft.ProgressRing(width=20, height=20, stroke_width=2, color=t.ACCENT, visible=False)

    def load_data():
        nonlocal projects
        try:
            projects = api.list_projects()
            for p in projects:
                try:
                    tasks = api.list_tasks(p["id"])
                    all_tasks[p["id"]] = tasks
                except ApiError:
                    all_tasks[p["id"]] = []
        except ApiError as err:
            if err.status_code == 401:
                page.go("/login")
                return
        render()
        page.update()

    def render():
        content_col.controls.clear()

        total_tasks = sum(len(tl) for tl in all_tasks.values())
        completed = sum(1 for tl in all_tasks.values() for tk in tl if tk["status"] == "completed")
        in_progress = sum(1 for tl in all_tasks.values() for tk in tl if tk["status"] == "in_progress")
        not_started = sum(1 for tl in all_tasks.values() for tk in tl if tk["status"] == "not_started")
        blocked = sum(1 for tl in all_tasks.values() for tk in tl if tk["status"] == "blocked")
        completion_pct = round((completed / total_tasks) * 100) if total_tasks > 0 else 0

        # Summary cards
        content_col.controls.append(t.heading_2("Portfolio Overview"))
        content_col.controls.append(ft.Container(height=t.SP_4))
        content_col.controls.append(ft.Row([
            _metric_card("Total Tasks", str(total_tasks), t.TEXT_PRIMARY),
            _metric_card("Completion Rate", f"{completion_pct}%", t.SUCCESS if completion_pct >= 50 else t.WARNING),
            _metric_card("At Risk", str(blocked), t.ERROR if blocked > 0 else t.SUCCESS),
            _metric_card("Active Projects", str(len(projects)), t.INFO),
        ], spacing=t.SP_4))
        content_col.controls.append(ft.Container(height=t.SP_7))

        # Status distribution
        content_col.controls.append(t.heading_3("Task Status Distribution"))
        content_col.controls.append(ft.Container(height=t.SP_3))

        if total_tasks > 0:
            bar = ft.Row([
                ft.Container(
                    width=max((completed / total_tasks) * 600, 2) if completed > 0 else 0,
                    height=32, bgcolor=t.SUCCESS,
                    border_radius=ft.border_radius.only(top_left=6, bottom_left=6),
                    tooltip=f"Completed: {completed}",
                ),
                ft.Container(
                    width=max((in_progress / total_tasks) * 600, 2) if in_progress > 0 else 0,
                    height=32, bgcolor=t.INFO, tooltip=f"In Progress: {in_progress}",
                ),
                ft.Container(
                    width=max((not_started / total_tasks) * 600, 2) if not_started > 0 else 0,
                    height=32, bgcolor="#d1d5db", tooltip=f"Not Started: {not_started}",
                ),
                ft.Container(
                    width=max((blocked / total_tasks) * 600, 2) if blocked > 0 else 0,
                    height=32, bgcolor=t.ERROR,
                    border_radius=ft.border_radius.only(top_right=6, bottom_right=6),
                    tooltip=f"Blocked: {blocked}",
                ),
            ], spacing=1)
            content_col.controls.append(t.card_container(ft.Column([
                bar, ft.Container(height=t.SP_3),
                ft.Row([
                    _legend_dot(t.SUCCESS, f"Completed ({completed})"),
                    _legend_dot(t.INFO, f"In Progress ({in_progress})"),
                    _legend_dot("#d1d5db", f"Not Started ({not_started})"),
                    _legend_dot(t.ERROR, f"Blocked ({blocked})"),
                ], spacing=t.SP_5),
            ])))
        else:
            content_col.controls.append(t.card_container(
                ft.Container(content=t.body_secondary("No tasks to visualize."), padding=t.SP_6, alignment=ft.Alignment.CENTER)
            ))

        content_col.controls.append(ft.Container(height=t.SP_7))

        # Per-project breakdown
        content_col.controls.append(t.heading_3("Project Breakdown"))
        content_col.controls.append(ft.Container(height=t.SP_3))

        if not projects:
            content_col.controls.append(t.card_container(
                ft.Container(content=t.body_secondary("No projects yet."), padding=t.SP_6, alignment=ft.Alignment.CENTER)
            ))
        else:
            project_rows = []
            for p in projects:
                ptasks = all_tasks.get(p["id"], [])
                total = len(ptasks)
                done = sum(1 for tk in ptasks if tk["status"] == "completed")
                blk = sum(1 for tk in ptasks if tk["status"] == "blocked")
                pct = round((done / total) * 100) if total > 0 else 0

                bar_fill = ft.Container(width=max(pct * 3, 0), height=12, bgcolor=t.SUCCESS if blk == 0 else t.WARNING, border_radius=6)
                bar_bg = ft.Container(
                    content=ft.Stack([
                        ft.Container(width=300, height=12, bgcolor=t.DIVIDER, border_radius=6),
                        bar_fill,
                    ]),
                    width=300,
                )

                project_rows.append(ft.Row([
                    ft.Text(p.get("name", ""), size=14, weight=ft.FontWeight.W_500, color=t.TEXT_PRIMARY, font_family=t.FONT_FAMILY, width=180, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    bar_bg,
                    ft.Text(f"{pct}%", size=13, color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY, width=45),
                    ft.Text(f"{done}/{total}", size=13, color=t.TEXT_TERTIARY, font_family=t.FONT_FAMILY, width=50),
                    t.status_badge("blocked") if blk > 0 else ft.Container(),
                ], spacing=t.SP_4, vertical_alignment=ft.CrossAxisAlignment.CENTER))

            content_col.controls.append(t.card_container(ft.Column(project_rows, spacing=t.SP_4)))

        content_col.controls.append(ft.Container(height=t.SP_7))

        # Priority distribution
        content_col.controls.append(t.heading_3("Priority Distribution"))
        content_col.controls.append(ft.Container(height=t.SP_3))

        priorities = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for tl in all_tasks.values():
            for tk in tl:
                pri = tk.get("priority", "medium")
                priorities[pri] = priorities.get(pri, 0) + 1

        if total_tasks > 0:
            pri_bars = []
            for pri_name, pri_count in priorities.items():
                if pri_count == 0:
                    continue
                pct = round((pri_count / total_tasks) * 100)
                pri_bars.append(ft.Row([
                    ft.Container(content=ft.Text(pri_name.title(), size=12, color=t.PRIORITY_COLORS[pri_name], font_family=t.FONT_FAMILY), width=70),
                    ft.Container(content=ft.Container(width=max(pct * 4, 4), height=20, bgcolor=t.PRIORITY_COLORS[pri_name], border_radius=4)),
                    ft.Text(f"{pri_count} ({pct}%)", size=12, color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY),
                ], spacing=t.SP_3, vertical_alignment=ft.CrossAxisAlignment.CENTER))
            content_col.controls.append(t.card_container(ft.Column(pri_bars, spacing=t.SP_3)))
        else:
            content_col.controls.append(t.card_container(
                ft.Container(content=t.body_secondary("No tasks to analyze."), padding=t.SP_6, alignment=ft.Alignment.CENTER)
            ))

        content_col.controls.append(ft.Container(height=t.SP_7))

        # AI risk analysis
        content_col.controls.append(t.heading_3("AI Risk Analysis"))
        content_col.controls.append(ft.Container(height=t.SP_3))
        content_col.controls.append(t.card_container(ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.WARNING_AMBER_OUTLINED, size=18, color=t.WARNING),
                    width=36, height=36, bgcolor=t.WARNING_BG, border_radius=t.RADIUS_MD, alignment=ft.Alignment.CENTER,
                ),
                t.heading_3("Automated Risk Assessment"),
                ft.Container(expand=True),
                risk_loading,
            ], spacing=t.SP_3, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(height=t.SP_2),
            ft.Row([t.outlined_button("Analyze All Projects", on_click=lambda e: run_risk_analysis(), icon=ft.Icons.AUTO_AWESOME_OUTLINED)]),
            ft.Container(height=t.SP_3),
            risk_text,
        ])))

    def run_risk_analysis():
        risk_loading.visible = True
        risk_text.value = ""
        page.update()

        results = []
        for p in projects:
            try:
                data = api.ai_summary(p["id"], "risks")
                results.append(f"[ {p['name']} ]\n{data.get('result', 'No data')}")
            except ApiError as err:
                results.append(f"[ {p['name']} ]\nError: {err}")

        risk_text.value = "\n\n".join(results) if results else "No projects to analyze."
        risk_loading.visible = False
        page.update()

    content_col = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
    main_area = ft.Container(content=content_col, padding=t.SP_8, expand=True, bgcolor=t.BG)

    load_data()

    return ft.Column([main_area], expand=True)


def _metric_card(label, value, color):
    return ft.Container(
        content=ft.Column([
            t.label_text(label),
            ft.Text(value, size=36, weight=ft.FontWeight.W_700, color=color, font_family=t.FONT_FAMILY),
        ], spacing=t.SP_1),
        bgcolor=t.CARD, border=ft.border.all(1, t.CARD_BORDER), border_radius=t.RADIUS_LG,
        padding=ft.padding.symmetric(horizontal=t.SP_6, vertical=t.SP_5), expand=True,
    )


def _legend_dot(color, label):
    return ft.Row([
        ft.Container(width=10, height=10, bgcolor=color, border_radius=50),
        ft.Text(label, size=12, color=t.TEXT_SECONDARY, font_family=t.FONT_FAMILY),
    ], spacing=t.SP_2)
