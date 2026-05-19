# PuddingUnityMCP — Fork Notes

This fork of [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp) adds **server-side token saver middleware**, so MCP clients (Claude, Codex, Cursor, etc.) do not have to install a separate proxy to control token cost.

Upstream behaviour is unchanged when no fork env vars are set. Setting any of them turns the saver on.

## Why this fork exists

[MCPzip](https://github.com/love0835/MCPzip) measured CoplayDev/unity-mcp v9.4.8 and found the same MCP traffic could be reduced **>90%** via four strategies (tool whitelist, query limits, semantic compression, summary+reference). MCPzip implemented those as an external proxy. This fork moves the strategies **inside the server**, so every client that connects automatically benefits — no per-client proxy install.

## What changed vs upstream

| Area | File | Change |
|---|---|---|
| Config dataclass | `Server/src/core/config.py` | 5 new fields under `ServerConfig` |
| Env var parsing | `Server/src/main.py` | Parse `UNITY_MCP_ENABLED_TOOLS` etc. into `config` |
| Middleware (new) | `Server/src/transport/token_saver_middleware.py` | `PuddingTokenSaverMiddleware` |
| Policy helpers (new) | `Server/src/transport/token_saver_policies.py` | Pure functions: summarize, semantic compress, sha256 reference |
| Middleware registration | `Server/src/main.py` | `mcp.add_middleware(PuddingTokenSaverMiddleware())` |
| Resource whitelist | `Server/src/services/resources/__init__.py` | Skip resources outside `UNITY_MCP_ENABLED_RESOURCES` at registration time |
| Tests (new) | `Server/tests/test_token_saver_policies.py` | 15 tests — policy functions + middleware behaviour |

No upstream files were rewritten — only additive edits to `main.py`, `core/config.py`, and `services/resources/__init__.py`. The middleware is a no-op until env vars are set.

## Configuration

All settings are environment variables, set wherever the MCP server is launched (Unity's `Start Server` UI passes env to the spawned Python process; MCP clients that spawn the server can set env too).

| Env var | Default | Effect |
|---|---|---|
| `UNITY_MCP_ENABLED_TOOLS` | unset | Comma-separated tool name whitelist; `tools/list` returns only matching tools. Hidden tools cannot be called. |
| `UNITY_MCP_ENABLED_RESOURCES` | unset | Comma-separated resource URI **or** name whitelist; non-matching resources are not registered. |
| `UNITY_MCP_RESPONSE_POLICY` | `raw` | One of `raw`, `summary_reference`, `semantic_compression`. Applies to tool results and resource reads that exceed the threshold. |
| `UNITY_MCP_RESPONSE_THRESHOLD_TOKENS` | `1200` | Estimated tokens (`bytes/4`) above which the policy kicks in. Smaller responses pass through unchanged. |
| `UNITY_MCP_RESPONSE_STORE_DIR` | unset | Directory where `summary_reference` writes original payloads (one `<sha256>.txt` per response). Disabled when unset. |
| `UNITY_MCP_LANG` | `en` | Tool schema language. Set to `zh_TW` for full Traditional Chinese (Taiwan). Unrecognized values fall back to `en`. |

### Policy behaviours

- **`raw`** — middleware is a no-op for responses. Use this with `UNITY_MCP_ENABLED_TOOLS` alone to get pure schema gating.
- **`semantic_compression`** — deduplicates lines, caps stack traces at 6 frames, truncates at ~2,400 chars. Original is **not** retained.
- **`summary_reference`** — replaces large text with sha256 + URI + 12-line head summary. If `UNITY_MCP_RESPONSE_STORE_DIR` is set, the original is written to disk so it can be retrieved out-of-band.

## Recommended starting profile (UnityMCP)

Based on MCPzip's measurements on `MaoCardBattlePrototype` (Codex side):

```bash
export UNITY_MCP_ENABLED_TOOLS="find_gameobjects,read_console,manage_scene"
export UNITY_MCP_ENABLED_RESOURCES="mcpforunity://editor/state,mcpforunity://instances"
export UNITY_MCP_RESPONSE_POLICY="semantic_compression"
export UNITY_MCP_RESPONSE_THRESHOLD_TOKENS="1200"
```

Expected savings: MCP traffic **~93%**, Codex agent total **~66%**. Tune the whitelist for your workflow.

## Side effects to be aware of

| Setting | Side effect | Mitigation |
|---|---|---|
| `ENABLED_TOOLS` | Agent cannot call hidden tools (gets "tool not found") | Whitelist must cover everything you need; widen for debug sessions |
| `RESPONSE_POLICY=semantic_compression` | Repeated log lines collapsed; stack traces capped at 6 frames; long output truncated at ~2,400 chars | Use `raw` while debugging concrete errors |
| `RESPONSE_POLICY=summary_reference` | Agent sees only a 12-line summary + sha256 URI; URI is informational only (no resolver) | Set `UNITY_MCP_RESPONSE_STORE_DIR` so the original is on disk for human review |
| `ENABLED_RESOURCES` | Filtered at registration time, so non-whitelisted resources are not even advertised | Restart server to pick up whitelist changes |

## Language / i18n

Set `UNITY_MCP_LANG=zh_TW` to get **Traditional Chinese (Taiwan) tool schemas**. Coverage:

- All 39 tools — `description`, `ToolAnnotations.title`, every `Annotated[T, "..."]` parameter description
- The high-level `_build_instructions()` text
- The 9 `TOOL_GROUPS` descriptions

The translation layer mutates `func.__annotations__` at decorator time before FastMCP reads the schema, so MCP clients (Claude, Codex, Cursor) see Chinese natively — no extra config on the client side.

**Behaviour:**
- Default `en` is a complete no-op — original strings reach FastMCP unchanged.
- Missing translations (e.g. an upstream tool added after the translation table was written) fall back to English silently. No errors, no warnings.
- Translations live in `Server/src/transport/translations/zh_TW.py` (which composes `_batch1`–`_batch4` and `_meta`). Edit those files to fix wording.

**Adding a new language:**
1. Create `Server/src/transport/translations/<bcp47>.py` (e.g. `ja_JP.py`).
2. Export `TOOL_TRANSLATIONS` (dict keyed by tool name) and optionally `INSTRUCTIONS`, `GROUP_TRANSLATIONS`.
3. Each tool entry follows: `{"description": "...", "title": "...", "params": {"param_name": "...", ...}}`. All keys are optional — supply only what you want translated.
4. Set `UNITY_MCP_LANG=ja_JP` to activate.

## Relationship to upstream `manage_tools`

Upstream v9.4.8 added a `manage_tools` tool that can enable/disable tool *groups* dynamically. PuddingTokenSaver's `UNITY_MCP_ENABLED_TOOLS` operates at a lower layer (individual tool name whitelist) and is applied **on top** of upstream's group filtering — the two compose without conflict.

## Run the tests

```bash
cd Server
python -m pytest tests/test_token_saver_policies.py -v
```

15 tests cover the policy functions (pure functions, no FastMCP) and middleware behaviour (mocked `call_next`).

## Future work / PR upstream

The fork is intentionally additive so a PR to upstream is feasible:

1. Move `transport/token_saver_*` to a clearly named subpackage (e.g. `transport/token_saver/`).
2. Document the env vars in the upstream README (Environment Variables section).
3. Add an opt-in flag if upstream prefers strict opt-in over "no-op when unset".
4. Discuss whether `summary_reference` URIs should become real readable resources (it would require an extra resource registration).

## License

Same as upstream — MIT. See `LICENSE`.
