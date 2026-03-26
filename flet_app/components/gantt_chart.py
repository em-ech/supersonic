"""Gantt chart component built from Flet containers."""

from datetime import date, timedelta
from typing import Optional

import flet as ft
from flet_app import theme as t

CHART_WIDTH = 700
ROW_HEIGHT = 32
ROW_GAP = 6
LABEL_WIDTH = 180


def _parse_date(val: Optional[str]) -> Optional[date]:
    if not val:
        return None
    try:
        return date.fromisoformat(val[:10])
    except (ValueError, TypeError):
        return None


def gantt_chart(tasks: list[dict]) -> ft.Control:
    """Render a Gantt chart for the given tasks.

    Tasks without both start_date and end_date are listed separately
    at the bottom as 'unscheduled'.
    """
    scheduled = []
    unscheduled = []

    for tk in tasks:
        start = _parse_date(tk.get("start_date"))
        end = _parse_date(tk.get("end_date"))
        if start or end:
            # Default: if only one date, make it a 1-day bar
            if not start:
                start = end
            if not end:
                end = start
            if end < start:
                start, end = end, start
            scheduled.append({**tk, "_start": start, "_end": end})
        else:
            unscheduled.append(tk)

    if not scheduled and not unscheduled:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.BAR_CHART_OUTLINED, size=40, color=t.TEXT_TERTIARY),
                    t.heading_3("No tasks to chart"),
                    t.body_secondary("Add tasks with start and end dates to see the Gantt chart."),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=t.SP_2,
            ),
            padding=t.SP_10,
            alignment=ft.Alignment.CENTER,
        )

    # Compute date range
    all_starts = [tk["_start"] for tk in scheduled]
    all_ends = [tk["_end"] for tk in scheduled]
    range_start = min(all_starts)
    range_end = max(all_ends)
    total_days = max((range_end - range_start).days, 1)

    # Sort by start date, then by end date
    scheduled.sort(key=lambda tk: (tk["_start"], tk["_end"]))

    # Build header with month markers
    header_controls = _build_header(range_start, range_end, total_days)

    # Build rows
    rows = []
    for tk in scheduled:
        row = _build_row(tk, range_start, total_days)
        rows.append(row)

    chart_body = ft.Column(rows, spacing=ROW_GAP)

    chart_section = ft.Column(
        [
            header_controls,
            ft.Container(height=t.SP_2),
            chart_body,
        ],
        spacing=0,
    )

    sections = [chart_section]

    # Unscheduled tasks
    if unscheduled:
        unsched_rows = []
        for tk in unscheduled:
            status = tk.get("status", "not_started")
            unsched_rows.append(
                ft.Row(
                    [
                        ft.Container(
                            width=9, height=9,
                            bgcolor=t.STATUS_COLORS.get(status, t.TEXT_TERTIARY),
                            border_radius=50,
                        ),
                        ft.Text(
                            tk.get("title", ""),
                            size=13, color=t.TEXT_PRIMARY, font_family=t.FONT_FAMILY,
                            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        t.status_badge(status),
                    ],
                    spacing=t.SP_3,
                )
            )

        sections.append(ft.Container(height=t.SP_6))
        sections.append(t.body_secondary("Unscheduled (no dates set)"))
        sections.append(ft.Container(height=t.SP_2))
        sections.append(
            t.card_container(ft.Column(unsched_rows, spacing=t.SP_3))
        )

    return ft.Column(sections, spacing=0, scroll=ft.ScrollMode.AUTO)


def _build_header(range_start: date, range_end: date, total_days: int) -> ft.Control:
    """Build a date header row with month labels and day ticks."""
    # Generate month boundaries
    markers = []
    current = range_start.replace(day=1)
    while current <= range_end:
        if current >= range_start:
            offset_days = (current - range_start).days
            x = (offset_days / total_days) * CHART_WIDTH
            markers.append((x, current.strftime("%b %Y")))
        # Next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    # If no month boundary falls in range, show start and end
    if not markers:
        markers = [
            (0, range_start.strftime("%b %d")),
            (CHART_WIDTH - 60, range_end.strftime("%b %d")),
        ]

    header_stack = ft.Stack(
        controls=[
            ft.Container(
                content=ft.Text(
                    label, size=10, color=t.TEXT_TERTIARY, font_family=t.FONT_FAMILY,
                ),
                left=x,
                top=0,
            )
            for x, label in markers
        ],
        height=18,
        width=CHART_WIDTH,
    )

    # Date range label
    range_label = ft.Text(
        f"{range_start.strftime('%b %d, %Y')}  to  {range_end.strftime('%b %d, %Y')}",
        size=11, color=t.TEXT_TERTIARY, font_family=t.FONT_FAMILY,
    )

    return ft.Column(
        [
            range_label,
            ft.Container(height=t.SP_1),
            ft.Row(
                [ft.Container(width=LABEL_WIDTH), header_stack],
                spacing=t.SP_3,
            ),
            ft.Divider(height=1, color=t.DIVIDER),
        ],
        spacing=t.SP_1,
    )


def _build_row(tk: dict, range_start: date, total_days: int) -> ft.Control:
    """Build a single Gantt row: label + bar."""
    status = tk.get("status", "not_started")
    bar_color = t.STATUS_COLORS.get(status, t.TEXT_TERTIARY)
    title = tk.get("title", "")
    assignee = tk.get("assignee") or ""
    start: date = tk["_start"]
    end: date = tk["_end"]

    offset_days = (start - range_start).days
    duration = max((end - start).days, 1)

    bar_left = (offset_days / total_days) * CHART_WIDTH
    bar_width = max((duration / total_days) * CHART_WIDTH, 8)  # min 8px

    # Label column
    label = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    title, size=12, weight=ft.FontWeight.W_500,
                    color=t.TEXT_PRIMARY, font_family=t.FONT_FAMILY,
                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Text(
                    assignee, size=10, color=t.TEXT_TERTIARY, font_family=t.FONT_FAMILY,
                    visible=bool(assignee),
                ),
            ],
            spacing=0,
        ),
        width=LABEL_WIDTH,
    )

    # Date label on the bar
    date_label = f"{start.strftime('%b %d')} - {end.strftime('%b %d')}"

    bar = ft.Container(
        content=ft.Text(
            date_label if bar_width > 80 else "",
            size=9, color=t.TEXT_ON_ACCENT, font_family=t.FONT_FAMILY,
        ),
        bgcolor=bar_color,
        border_radius=4,
        height=ROW_HEIGHT,
        width=bar_width,
        padding=ft.padding.symmetric(horizontal=6, vertical=2),
        tooltip=f"{title}\n{date_label}\n{status.replace('_', ' ').title()}",
        alignment=ft.Alignment.CENTER_LEFT,
    )

    # Track background + bar
    track = ft.Stack(
        controls=[
            # Background track
            ft.Container(
                width=CHART_WIDTH, height=ROW_HEIGHT,
                bgcolor=t.DIVIDER, border_radius=4,
            ),
            # Bar positioned
            ft.Container(
                content=bar,
                left=bar_left,
                top=0,
            ),
        ],
        height=ROW_HEIGHT,
        width=CHART_WIDTH,
    )

    return ft.Row([label, track], spacing=t.SP_3, vertical_alignment=ft.CrossAxisAlignment.CENTER)
