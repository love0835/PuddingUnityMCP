"""
Traditional Chinese (Taiwan) translations for PuddingUnityMCP tool schemas.

This module is the public entry point for ``UNITY_MCP_LANG=zh_TW``. It composes
``TOOL_TRANSLATIONS`` from per-batch modules (``_batch1`` … ``_batch4``) and pulls
high-level instructions + group descriptions from ``_meta``.

Batch files are populated by ``codex exec`` workers (see PUDDING.md). Missing
batches degrade gracefully — the i18n layer falls back to English silently.
"""
from __future__ import annotations

import importlib
from typing import Any

_BATCH_MODULES = ("_batch1", "_batch2", "_batch3", "_batch4")
_BATCH_VAR_NAMES = ("BATCH_1", "BATCH_2", "BATCH_3", "BATCH_4")


def _load_all_batches() -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for mod_name, var_name in zip(_BATCH_MODULES, _BATCH_VAR_NAMES):
        try:
            module = importlib.import_module(f"transport.translations.{mod_name}")
        except ImportError:
            continue
        table = getattr(module, var_name, None)
        if isinstance(table, dict):
            merged.update(table)
    return merged


def _load_meta() -> tuple[dict[str, str] | str | None, dict[str, str]]:
    try:
        module = importlib.import_module("transport.translations._meta")
    except ImportError:
        return None, {}
    instructions = getattr(module, "INSTRUCTIONS_BY_SCOPE", None)
    if instructions is None:
        instructions = getattr(module, "INSTRUCTIONS", None)
    groups = getattr(module, "GROUP_TRANSLATIONS", {})
    if not isinstance(groups, dict):
        groups = {}
    return instructions, groups


TOOL_TRANSLATIONS: dict[str, dict[str, Any]] = _load_all_batches()
INSTRUCTIONS, GROUP_TRANSLATIONS = _load_meta()
