"""
PuddingUnityMCP token saver middleware.

Three hooks reduce the token cost of MCP traffic without touching the upstream
fastmcp library:

- ``on_list_tools`` filters the advertised tool set to ``UNITY_MCP_ENABLED_TOOLS``.
- ``on_call_tool`` rewrites large text content in tool results per ``UNITY_MCP_RESPONSE_POLICY``.
- ``on_read_resource`` does the same for resource reads.

The middleware is a no-op when no env vars are set, so installing it does not
change upstream behaviour. Enable via:

    UNITY_MCP_ENABLED_TOOLS=find_gameobjects,read_console
    UNITY_MCP_RESPONSE_POLICY=semantic_compression
    UNITY_MCP_RESPONSE_THRESHOLD_TOKENS=1200
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastmcp.server.middleware import Middleware, MiddlewareContext

from core.config import config
from transport.token_saver_policies import VALID_POLICIES, apply_policy

logger = logging.getLogger("mcp-for-unity-server")
_diag = logging.getLogger("transport.token_saver_middleware")


class PuddingTokenSaverMiddleware(Middleware):
    """FastMCP middleware that filters tool listings and compresses large responses."""

    def __init__(self) -> None:
        self._enabled_tools: set[str] = set(config.enabled_tools or ())
        self._policy: str = config.response_policy if config.response_policy in VALID_POLICIES else "raw"
        self._threshold: int = max(0, int(config.response_threshold_tokens or 0))
        self._store_dir: Path | None = (
            Path(config.response_store_dir).expanduser().resolve()
            if config.response_store_dir
            else None
        )
        if self._enabled_tools or self._policy != "raw":
            logger.info(
                "PuddingTokenSaver active: enabled_tools=%s policy=%s threshold=%d store_dir=%s",
                sorted(self._enabled_tools) or "<all>",
                self._policy,
                self._threshold,
                str(self._store_dir) if self._store_dir else "<none>",
            )

    async def on_list_tools(self, context: MiddlewareContext, call_next):
        tools = await call_next(context)
        if not self._enabled_tools:
            return tools
        filtered = [t for t in tools if getattr(t, "name", None) in self._enabled_tools]
        _diag.debug(
            "PuddingTokenSaver.on_list_tools: %d -> %d (whitelist=%s)",
            len(tools), len(filtered), sorted(self._enabled_tools),
        )
        return filtered

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        result = await call_next(context)
        if self._policy == "raw":
            return result
        self._transform_content(getattr(result, "content", None), label="tool")
        return result

    async def on_read_resource(self, context: MiddlewareContext, call_next):
        result = await call_next(context)
        if self._policy == "raw":
            return result
        # FastMCP read_resource may return a list, a single content, or an object with .contents.
        if isinstance(result, list):
            self._transform_content(result, label="resource")
        else:
            self._transform_content(getattr(result, "contents", None), label="resource")
            if hasattr(result, "text") and not getattr(result, "contents", None):
                new_text, transformed = apply_policy(
                    result.text or "",
                    policy=self._policy,
                    threshold_tokens=self._threshold,
                    store_dir=self._store_dir,
                )
                if transformed:
                    try:
                        result.text = new_text
                    except AttributeError:
                        pass
        return result

    def _transform_content(self, content, *, label: str) -> None:
        if not content:
            return
        for item in content:
            text = getattr(item, "text", None)
            if not isinstance(text, str) or not text:
                continue
            new_text, transformed = apply_policy(
                text,
                policy=self._policy,
                threshold_tokens=self._threshold,
                store_dir=self._store_dir,
            )
            if transformed:
                try:
                    item.text = new_text
                except AttributeError:
                    continue
                _diag.debug(
                    "PuddingTokenSaver: %s response transformed by policy=%s (chars %d -> %d)",
                    label, self._policy, len(text), len(new_text),
                )
