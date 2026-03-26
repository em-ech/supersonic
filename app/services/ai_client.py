"""
Pluggable AI client backed by Claude (Anthropic).

The public functions `generate_summary` and `generate_suggestions` accept
project context (serialised task data) and return natural-language text.

Uses the Anthropic Python SDK. Set ANTHROPIC_API_KEY in .env.
Falls back to a stub response if the key is not configured.
"""

from __future__ import annotations

import datetime
import os
from typing import Any


# ---- internal helper ----

async def _call_llm(system_prompt: str, user_prompt: str) -> str:
    """Call Claude via the Anthropic SDK. Falls back to stub if no API key."""
    api_key = os.environ.get("AI_API_KEY", "") or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key or api_key in ("not-set", "not-needed-for-stub"):
        return (
            "[AI stub response]\n\n"
            f"System context: {system_prompt[:120]}...\n"
            f"User query: {user_prompt[:120]}...\n\n"
            "This is a placeholder. Set ANTHROPIC_API_KEY in .env to enable Claude."
        )

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


# ---- helpers to build context from task data ----

def _tasks_to_text(tasks: list[dict[str, Any]]) -> str:
    if not tasks:
        return "No tasks found for this project."
    lines: list[str] = []
    for t in tasks:
        end = t.get("end_date")
        end_str = end.isoformat() if isinstance(end, datetime.datetime) else str(end) if end else "no deadline"
        lines.append(
            f"- {t['title']} | status={t['status']} priority={t['priority']} "
            f"assignee={t.get('assignee', 'unassigned')} due={end_str}"
        )
    return "\n".join(lines)


# ---- public API ----

async def generate_summary(
    project_name: str,
    tasks: list[dict[str, Any]],
    focus: str | None = None,
) -> str:
    system_prompt = (
        "You are a project-management assistant. Summarize the project "
        "status, upcoming deadlines, and potential risks. Be concise and actionable."
    )
    focus_text = f" Focus on: {focus}." if focus else ""
    user_prompt = (
        f"Project: {project_name}\n"
        f"Tasks:\n{_tasks_to_text(tasks)}\n\n"
        f"Provide a concise summary.{focus_text}"
    )
    return await _call_llm(system_prompt, user_prompt)


async def generate_suggestions(
    project_name: str,
    tasks: list[dict[str, Any]],
    user_prompt_extra: str | None = None,
) -> str:
    system_prompt = (
        "You are a project-management assistant. Suggest concrete "
        "improvements to the schedule, priorities, or workload distribution. "
        "Be specific and actionable."
    )
    extra = f"\nUser request: {user_prompt_extra}" if user_prompt_extra else ""
    user_prompt = (
        f"Project: {project_name}\n"
        f"Tasks:\n{_tasks_to_text(tasks)}\n\n"
        f"Suggest improvements.{extra}"
    )
    return await _call_llm(system_prompt, user_prompt)
