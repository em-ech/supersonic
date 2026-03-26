"""HTTP client for the Supersonic FastAPI backend."""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx

from flet_app.state import AppState

BASE_URL = os.environ.get("SUPERSONIC_API_URL", "http://localhost:8002")
UPLOAD_TIMEOUT = 60.0


class ApiError(Exception):
    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


class ApiClient:
    """Wraps httpx with JWT auth from AppState."""

    def __init__(self, state: AppState) -> None:
        self.state = state
        self._client = httpx.Client(base_url=BASE_URL, timeout=15.0)

    def _headers(self) -> dict[str, str]:
        h: dict[str, str] = {}
        token = self.state.get_token()
        if token:
            h["Authorization"] = f"Bearer {token}"
        return h

    def _request(self, method: str, path: str, **kwargs) -> Any:
        try:
            resp = self._client.request(method, path, headers=self._headers(), **kwargs)
        except httpx.ConnectError:
            raise ApiError(f"Cannot reach the server. Is the backend running at {BASE_URL}?")

        if resp.status_code == 401:
            self.state.clear()
            raise ApiError("Session expired. Please sign in again.", 401)
        if resp.status_code == 204:
            return None

        try:
            data = resp.json()
        except Exception:
            if not resp.is_success:
                raise ApiError(f"Request failed ({resp.status_code})", resp.status_code)
            raise ApiError("Invalid response from server")

        if not resp.is_success:
            detail = data.get("detail", f"Request failed ({resp.status_code})") if isinstance(data, dict) else str(data)
            raise ApiError(str(detail), resp.status_code)
        return data

    # ── Auth ──

    def register(self, username: str, password: str, full_name: str = "") -> dict:
        body: dict[str, str] = {"username": username, "password": password}
        if full_name:
            body["full_name"] = full_name
        return self._request("POST", "/auth/register", json=body)

    def login(self, username: str, password: str) -> str:
        data = self._request("POST", "/auth/login", json={"username": username, "password": password})
        token = data["access_token"]
        self.state.set_token(token)
        return token

    def get_me(self) -> dict:
        return self._request("GET", "/auth/me")

    # ── Projects ──

    def list_projects(self) -> list[dict]:
        return self._request("GET", "/projects")

    def get_project(self, project_id: str) -> dict:
        return self._request("GET", f"/projects/{project_id}")

    def create_project(self, name: str, description: str = "") -> dict:
        body: dict[str, str] = {"name": name}
        if description:
            body["description"] = description
        return self._request("POST", "/projects", json=body)

    def update_project(self, project_id: str, name: Optional[str] = None, description: Optional[str] = None) -> dict:
        body: dict[str, str] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        return self._request("PUT", f"/projects/{project_id}", json=body)

    def delete_project(self, project_id: str) -> None:
        self._request("DELETE", f"/projects/{project_id}")

    def import_project(self, file_path: str, file_name: str) -> dict:
        """Upload a CSV/XLSX/XLS file to create a project with tasks."""
        content_type = "text/csv"
        if file_name.endswith(".xlsx"):
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif file_name.endswith(".xls"):
            content_type = "application/vnd.ms-excel"

        with open(file_path, "rb") as f:
            files = {"file": (file_name, f, content_type)}
            headers = self._headers()
            try:
                resp = self._client.post("/projects/import", files=files, headers=headers, timeout=UPLOAD_TIMEOUT)
            except httpx.ConnectError:
                raise ApiError("Cannot reach the server.")

        if resp.status_code == 401:
            self.state.clear()
            raise ApiError("Session expired.", 401)
        if not resp.is_success:
            try:
                detail = resp.json().get("detail", "Import failed")
            except Exception:
                detail = "Import failed"
            raise ApiError(str(detail), resp.status_code)
        return resp.json()

    # ── Tasks ──

    def list_tasks(self, project_id: str, status: Optional[str] = None, priority: Optional[str] = None) -> list[dict]:
        params: dict[str, str] = {}
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        return self._request("GET", f"/projects/{project_id}/tasks", params=params)

    def create_task(self, project_id: str, **fields) -> dict:
        return self._request("POST", f"/projects/{project_id}/tasks", json=fields)

    def update_task(self, task_id: str, **fields) -> dict:
        return self._request("PUT", f"/tasks/{task_id}", json=fields)

    def delete_task(self, task_id: str) -> None:
        self._request("DELETE", f"/tasks/{task_id}")

    # ── Messages ──

    def list_messages(self, project_id: str) -> list[dict]:
        return self._request("GET", f"/projects/{project_id}/messages")

    def create_message(self, project_id: str, **fields) -> dict:
        return self._request("POST", f"/projects/{project_id}/messages", json=fields)

    # ── AI ──

    def ai_summary(self, project_id: str, focus: Optional[str] = None) -> dict:
        body: dict[str, Any] = {"project_id": project_id}
        if focus:
            body["focus"] = focus
        return self._request("POST", "/ai/summary", json=body)

    def ai_suggestions(self, project_id: str, prompt: Optional[str] = None) -> dict:
        body: dict[str, Any] = {"project_id": project_id}
        if prompt:
            body["prompt"] = prompt
        return self._request("POST", "/ai/suggestions", json=body)

    def ai_chat(self, project_id: str, message: str) -> dict:
        return self._request("POST", "/ai/chat", json={"project_id": project_id, "message": message})

    # ── Health ──

    def health(self) -> dict:
        return self._request("GET", "/health")
