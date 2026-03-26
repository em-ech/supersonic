"""Centralized application state with JWT persistence."""

import json
import os
from pathlib import Path
from typing import Optional


_STATE_DIR = Path.home() / ".supersonic"
_TOKEN_FILE = _STATE_DIR / "token.json"


class AppState:
    """Holds auth token, current user, and selected project.

    JWT is persisted to ~/.supersonic/token.json so the user stays
    logged in between app launches.
    """

    def __init__(self) -> None:
        self.token: Optional[str] = None
        self.user: Optional[dict] = None
        self.selected_project: Optional[dict] = None
        self._load_token()

    # -- Token persistence --------------------------------------------------

    def _load_token(self) -> None:
        """Load saved JWT from disk if it exists."""
        try:
            if _TOKEN_FILE.exists():
                data = json.loads(_TOKEN_FILE.read_text())
                self.token = data.get("access_token")
        except (json.JSONDecodeError, OSError):
            self.token = None

    def _save_token(self) -> None:
        """Persist current JWT to disk."""
        try:
            _STATE_DIR.mkdir(parents=True, exist_ok=True)
            _TOKEN_FILE.write_text(json.dumps({"access_token": self.token}))
        except OSError:
            pass  # best-effort persistence

    def _clear_token_file(self) -> None:
        """Remove persisted token file."""
        try:
            if _TOKEN_FILE.exists():
                _TOKEN_FILE.unlink()
        except OSError:
            pass

    # -- Public API ---------------------------------------------------------

    def set_token(self, token: str) -> None:
        self.token = token
        self._save_token()

    def get_token(self) -> Optional[str]:
        return self.token

    def is_authenticated(self) -> bool:
        return self.token is not None

    def set_user(self, user: dict) -> None:
        self.user = user

    def get_user(self) -> Optional[dict]:
        return self.user

    def set_selected_project(self, project: Optional[dict]) -> None:
        self.selected_project = project

    def get_selected_project(self) -> Optional[dict]:
        return self.selected_project

    def clear(self) -> None:
        """Full logout: wipe memory and disk."""
        self.token = None
        self.user = None
        self.selected_project = None
        self._clear_token_file()
