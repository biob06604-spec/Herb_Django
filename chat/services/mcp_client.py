"""
MCP client used by the Django chat app.

Originally this project called MCP tools by spawning the local `mcp_server.py`
via stdio. For deployment, we switch to calling a remote Streamable HTTP MCP
endpoint (e.g. JD Cloud) via URL.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Tuple

import httpx


def _get_mcp_endpoint() -> str:
    """
    Remote MCP URL, example: https://<host>/mcp
    """
    return os.getenv("MCP_ENDPOINT", "http://127.0.0.1:8087/mcp").rstrip("/")


class StreamableHttpMcpClient:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.protocol_version = os.getenv("MCP_PROTOCOL_VERSION", "2025-12-05")
        # Some deployments validate the Host header strictly (and may return 421).
        # Allow overriding it explicitly when needed (e.g. behind a proxy).
        self.host_header = os.getenv("MCP_HOST_HEADER", "")
        self.session_id: str | None = None
        self._client = httpx.Client(timeout=httpx.Timeout(120.0))

    def close(self) -> None:
        self._client.close()

    def _headers(self) -> Dict[str, str]:
        # Some MCP servers require the client to accept both JSON and SSE.
        headers = {"Accept": "application/json, text/event-stream"}
        if self.host_header:
            headers["Host"] = self.host_header
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        return headers

    def _parse_response_json(self, r: httpx.Response) -> Dict[str, Any]:
        """
        The streamable-http transport may respond in JSON or SSE (`text/event-stream`).
        We normalize both to a dict.
        """
        ctype = (r.headers.get("content-type") or "").lower()
        if "text/event-stream" in ctype:
            # SSE format: `event: message` + `data: {...}`
            for line in r.text.splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith("data:"):
                    data = line[len("data:") :].strip()
                    if not data:
                        continue
                    try:
                        return json.loads(data)
                    except json.JSONDecodeError:
                        continue
            return {}
        return r.json()

    def _post_json(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = self._client.post(self.endpoint, json=payload, headers=self._headers())
        if r.status_code == 204 or not r.content:
            return {}
        r.raise_for_status()
        return self._parse_response_json(r)

    def initialize(self) -> None:
        init_req: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": self.protocol_version,
                "capabilities": {},
                "clientInfo": {"name": "herbapi-django", "version": "0.1"},
            },
        }
        # Initialize must be called without a session id; we capture it from response headers.
        r = self._client.post(self.endpoint, json=init_req, headers=self._headers())
        if r.status_code == 204 or not r.content:
            raise RuntimeError("Initialize returned empty response")
        r.raise_for_status()
        self.session_id = r.headers.get("mcp-session-id") or self.session_id
        res = self._parse_response_json(r)
        if "error" in res:
            raise RuntimeError(f"Initialize error: {res['error']}")
        self._post_json({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def call_tool_stream(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Call MCP tool using streamable-http. We concatenate all text chunks, and
        also try to keep structuredContent if present.
        """
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments or {}},
        }

        status_code = 200
        collected_text: List[str] = []
        structured: Dict[str, Any] | None = None

        with self._client.stream(
            "POST",
            self.endpoint,
            json=req,
            headers=self._headers(),
        ) as resp:
            status_code = resp.status_code
            if status_code != 200:
                return {"error": f"HTTP Error {status_code}"}, status_code

            for line in resp.iter_lines():
                if not line:
                    continue
                line = line.strip()
                if line.startswith("event:"):
                    continue
                if line.startswith("data:"):
                    line = line[len("data:") :].strip()
                    if not line:
                        continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if "error" in chunk:
                    msg = chunk["error"].get("message") if isinstance(chunk["error"], dict) else str(chunk["error"])
                    return {"error": msg}, 200

                if "result" in chunk:
                    result = chunk["result"] or {}
                    if structured is None and isinstance(result, dict) and result.get("structuredContent") is not None:
                        structured = result.get("structuredContent")

                    content = result.get("content") or []
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            collected_text.append(item.get("text", ""))

        if structured is not None:
            return structured, status_code

        text = "\n".join([t for t in collected_text if t])
        return {"content": text} if text else {"content": ""}, status_code


def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """
    Synchronous helper used by `agent_service.py`.
    """
    endpoint = _get_mcp_endpoint()
    client = StreamableHttpMcpClient(endpoint)
    try:
        client.initialize()
        result, _status = client.call_tool_stream(tool_name, arguments or {})
        return result
    finally:
        client.close()