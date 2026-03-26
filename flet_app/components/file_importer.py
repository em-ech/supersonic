"""FilePicker wrapper for CSV/XLSX import (Flet 0.82.x desktop mode).

In Flet 0.82.x, FilePicker.pick_files() is async. We use
asyncio.create_task to call it from sync button handlers.
"""

import asyncio
from typing import Callable

import flet as ft

ALLOWED_EXTENSIONS = ["csv", "xlsx", "xls"]


class FileImporter:
    """Wraps ft.FilePicker for spreadsheet import.

    Usage:
        importer = FileImporter(page, on_import=handle_file)
        importer.pick()  # opens OS file dialog, calls on_import if file selected
    """

    def __init__(self, page: ft.Page, on_import: Callable[[str, str], None]) -> None:
        self._page = page
        self._on_import = on_import
        self._picker = ft.FilePicker()

    def pick(self) -> None:
        """Schedule the async file picker from a sync context."""
        asyncio.create_task(self._pick_async())

    async def _pick_async(self) -> None:
        """Open the OS file dialog and call on_import if a file is selected."""
        files = await self._picker.pick_files(
            dialog_title="Import project from spreadsheet",
            allowed_extensions=ALLOWED_EXTENSIONS,
            allow_multiple=False,
        )
        if not files:
            return
        picked = files[0]
        if picked.path and picked.name:
            self._on_import(picked.path, picked.name)
