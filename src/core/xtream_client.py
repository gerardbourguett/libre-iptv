from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any

_HEADERS = {
    "User-Agent": "LibreIPTV/1.0",
    "Accept": "application/json, */*",
}


@dataclass
class AccountInfo:
    username: str
    password: str
    status: str = ""
    exp_date: str = ""
    is_trial: bool = False
    active_cons: int = 0
    max_connections: int = 1
    allowed_output_formats: list[str] = field(default_factory=list)


class XtreamError(Exception):
    pass


class XtreamClient:
    def __init__(
        self,
        server: str,
        username: str,
        password: str,
        *,
        timeout: int = 30,
    ) -> None:
        self._server = server.rstrip("/")
        self._username = username
        self._password = password
        self._timeout = timeout

    def _base_params(self) -> dict[str, str]:
        return {"username": self._username, "password": self._password}

    def _api_url(self) -> str:
        return f"{self._server}/player_api.php"

    def _get(self, url: str, params: dict[str, str]) -> bytes:
        full_url = url + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(full_url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=self._timeout) as resp:
            return resp.read()

    def _get_json(self, url: str, params: dict[str, str]) -> Any:
        return json.loads(self._get(url, params))

    def account_info(self) -> AccountInfo:
        data = self._get_json(self._api_url(), self._base_params())
        ui: dict[str, Any] = data.get("user_info", {}) if isinstance(data, dict) else {}
        return AccountInfo(
            username=self._username,
            password=self._password,
            status=str(ui.get("status", "")),
            exp_date=str(ui.get("exp_date", "")),
            is_trial=bool(int(ui.get("is_trial", 0))),
            active_cons=int(ui.get("active_cons", 0)),
            max_connections=int(ui.get("max_connections", 1)),
            allowed_output_formats=list(ui.get("allowed_output_formats", [])),
        )

    def get_m3u_plus(self) -> str:
        params = {**self._base_params(), "type": "m3u_plus", "output": "m3u8"}
        return self._get(f"{self._server}/get.php", params).decode("utf-8")

    def get_xmltv(self) -> bytes:
        return self._get(f"{self._server}/xmltv.php", self._base_params())

    def get_live_categories(self) -> list[dict[str, Any]]:
        params = {**self._base_params(), "action": "get_live_categories"}
        result = self._get_json(self._api_url(), params)
        return list(result) if isinstance(result, list) else []

    def get_vod_categories(self) -> list[dict[str, Any]]:
        params = {**self._base_params(), "action": "get_vod_categories"}
        result = self._get_json(self._api_url(), params)
        return list(result) if isinstance(result, list) else []

    def get_vod_info(self, vod_id: int | str) -> dict[str, Any]:
        params = {**self._base_params(), "action": "get_vod_info", "vod_id": str(vod_id)}
        result = self._get_json(self._api_url(), params)
        return dict(result) if isinstance(result, dict) else {}

    def get_stream_url(self, stream_id: str, *, output: str = "m3u8") -> str:
        return f"{self._server}/play/{stream_id}/{output}"
