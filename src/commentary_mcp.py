from __future__ import annotations

import json
import subprocess
from typing import Any


MCP_URL = "https://mcp.soccerverse.io/mcp"


class SoccerverseMCPClient:
    """Minimal Soccerverse MCP client using the verified curl transport."""

    def __init__(
        self,
        url: str = MCP_URL,
        timeout: int = 30,
    ) -> None:
        self.url = url
        self.timeout = timeout
        self._request_id = 0

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _call(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }

        command = [
            "curl",
            "-sS",
            "--fail-with-body",
            "--max-time",
            str(self.timeout),
            "-H",
            "Content-Type: application/json",
            "-H",
            "Accept: application/json, text/event-stream",
            "-d",
            json.dumps(payload),
            self.url,
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout + 5,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or exc.stdout or "").strip()
            raise RuntimeError(
                f"MCP curl request failed: {detail[:500]}"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("MCP curl request timed out") from exc

        return self._parse_response(result.stdout)

    @staticmethod
    def _parse_response(body: str) -> Any:
        body = body.strip()

        if not body:
            raise RuntimeError("Empty MCP response")

        if body.startswith("{"):
            return SoccerverseMCPClient._extract_result(
                json.loads(body)
            )

        data_lines = [
            line[5:].strip()
            for line in body.splitlines()
            if line.startswith("data:")
        ]

        if not data_lines:
            raise RuntimeError(
                f"Unsupported MCP response format: {body[:200]}"
            )

        return SoccerverseMCPClient._extract_result(
            json.loads(data_lines[-1])
        )

    @staticmethod
    def _extract_result(payload: dict[str, Any]) -> Any:
        if "error" in payload:
            raise RuntimeError(str(payload["error"]))

        result = payload.get("result", payload)

        if not isinstance(result, dict):
            return result

        content = result.get("content")

        if not content:
            return result

        for item in content:
            if item.get("type") != "text":
                continue

            text = item.get("text", "")

            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text

        return result

    def resolve_club_name(self, name: str) -> Any:
        return self._call(
            "resolve_club_name",
            {"name": name},
        )

    def get_player_details(self, player_id: int) -> Any:
        return self._call("get_player_details", {"player_id": player_id})

    def get_club_schedule(self, club_id: int) -> Any:
        return self._call(
            "get_club_schedule",
            {"club_id": club_id},
        )

    def get_fixture(self, fixture_id: int) -> Any:
        return self._call(
            "get_fixture",
            {"fixture_id": fixture_id},
        )

    def get_match_events(self, fixture_id: int) -> Any:
        return self._call(
            "get_match_events",
            {"fixture_id": fixture_id},
        )

    def get_match_commentary(self, fixture_id: int) -> Any:
        return self._call(
            "get_match_commentary",
            {"fixture_id": fixture_id},
        )

    def get_match_subs(self, fixture_id: int) -> Any:
        return self._call(
            "get_match_subs",
            {"fixture_id": fixture_id},
        )
