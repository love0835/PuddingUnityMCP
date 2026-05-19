"""
PuddingUnityMCP fork: tool schema i18n layer.

Opt-in via ``UNITY_MCP_LANG`` env var (handled in main.py). When the language is
not the default "en", the decorator ``mcp_for_unity_tool`` calls
``apply_translation_to_func`` which:

1. Returns a translated ``description`` string for the tool (or the original).
2. Mutates ``func.__annotations__`` to swap each ``Annotated[T, "..."]`` metadata
   string with its translation, before FastMCP reads the schema.
3. Mutates ``tool_kwargs["annotations"].title`` if a ``ToolAnnotations`` was passed.

Translation tables live in sibling modules named after BCP47 tags (e.g. ``zh_TW.py``).
Each module exposes ``TOOL_TRANSLATIONS`` (dict keyed by tool name), optionally
``INSTRUCTIONS`` (str or tuple), and ``GROUP_TRANSLATIONS`` (dict). Missing entries
fall back to English silently — no error, no warning, so an out-of-sync table
never breaks the server.
"""
from __future__ import annotations

import logging
import typing
from typing import Annotated, Any, Callable

logger = logging.getLogger("mcp-for-unity-server")

_LANG_MODULES: dict[str, Any] = {}


def _load_lang(lang: str) -> Any | None:
    """Lazily import the translation module for ``lang`` (e.g. "zh_TW"). Returns None on miss."""
    if not lang or lang == "en":
        return None
    if lang in _LANG_MODULES:
        return _LANG_MODULES[lang]
    try:
        module = __import__(f"transport.translations.{lang}", fromlist=["TOOL_TRANSLATIONS"])
    except ImportError:
        _LANG_MODULES[lang] = None
        return None
    _LANG_MODULES[lang] = module
    return module


def get_translation(tool_name: str, lang: str) -> dict[str, Any] | None:
    """Return the translation dict for ``tool_name`` in ``lang``, or None if absent."""
    module = _load_lang(lang)
    if module is None:
        return None
    table = getattr(module, "TOOL_TRANSLATIONS", None)
    if not isinstance(table, dict):
        return None
    entry = table.get(tool_name)
    if not isinstance(entry, dict):
        return None
    return entry


def get_instructions_for_lang(lang: str, project_scoped_tools: bool) -> str | None:
    """Return the translated server instructions string for ``lang``, or None to fall back."""
    module = _load_lang(lang)
    if module is None:
        return None
    instructions = getattr(module, "INSTRUCTIONS", None)
    if isinstance(instructions, dict):
        key = "project_scoped" if project_scoped_tools else "default"
        return instructions.get(key) or instructions.get("default")
    if isinstance(instructions, str):
        return instructions
    return None


def _rewrite_annotated_metadata(func: Callable, params_zh: dict[str, str]) -> int:
    """Replace the description string inside ``Annotated[T, "..."]`` for each known param.

    Returns the number of params actually rewritten. Skips union types (e.g. ``str | None``)
    by walking into them where possible. Only mutates ``func.__annotations__`` — the source
    file is unchanged.
    """
    annotations = getattr(func, "__annotations__", None)
    if not isinstance(annotations, dict) or not params_zh:
        return 0

    rewritten = 0
    for name, annot in list(annotations.items()):
        if name not in params_zh:
            continue
        new_annot = _rewrite_annotation(annot, params_zh[name])
        if new_annot is not annot:
            annotations[name] = new_annot
            rewritten += 1
    return rewritten


def _rewrite_annotation(annot: Any, new_description: str) -> Any:
    """Recursively swap Annotated metadata strings inside ``annot``.

    Detection of ``Annotated[T, ...]`` is via the ``__metadata__`` attribute,
    because ``typing.get_origin`` strips the Annotated wrapper in Python 3.11+
    and returns the inner type directly.
    """
    metadata = getattr(annot, "__metadata__", None)
    if metadata:
        inner_type = getattr(annot, "__origin__", None)
        if inner_type is None:
            args = typing.get_args(annot)
            if not args:
                return annot
            inner_type = args[0]
        new_metadata: list[Any] = []
        replaced = False
        for m in metadata:
            if not replaced and isinstance(m, str):
                new_metadata.append(new_description)
                replaced = True
            else:
                new_metadata.append(m)
        if not replaced:
            return annot
        return Annotated[tuple([inner_type, *new_metadata])]

    origin = typing.get_origin(annot)

    # typing.Union[X, Y] form.
    if origin is typing.Union:
        args = typing.get_args(annot)
        new_args = tuple(_rewrite_annotation(a, new_description) for a in args)
        if new_args == args:
            return annot
        try:
            return typing.Union[new_args]  # type: ignore[index]
        except TypeError:
            return annot

    # PEP 604 unions (X | Y) report origin ``types.UnionType``.
    import types as _pytypes
    if isinstance(annot, _pytypes.UnionType):
        args = typing.get_args(annot)
        new_args = tuple(_rewrite_annotation(a, new_description) for a in args)
        if new_args == args:
            return annot
        rebuilt = new_args[0]
        for a in new_args[1:]:
            rebuilt = rebuilt | a
        return rebuilt

    return annot


def apply_translation_to_func(
    func: Callable,
    tool_name: str,
    description: str | None,
    tool_kwargs: dict[str, Any],
    lang: str,
) -> str | None:
    """Apply ``lang`` translations to ``func`` annotations + tool kwargs in place.

    Returns the translated description (or the original ``description`` if nothing matched).
    Safe to call with lang="en" — it's a no-op.
    """
    if not lang or lang == "en":
        return description

    entry = get_translation(tool_name, lang)
    if entry is None:
        return description

    # Title override (only when ToolAnnotations is present and writable).
    title = entry.get("title")
    if title:
        annotations_obj = tool_kwargs.get("annotations")
        if annotations_obj is not None:
            try:
                model_copy = getattr(annotations_obj, "model_copy", None)
                if callable(model_copy):
                    tool_kwargs["annotations"] = model_copy(update={"title": title})
                else:
                    setattr(annotations_obj, "title", title)
            except (AttributeError, TypeError):
                logger.debug(
                    "i18n: failed to set translated title on annotations for %s", tool_name
                )

    # Per-param Annotated metadata rewrite.
    params = entry.get("params")
    if isinstance(params, dict):
        _rewrite_annotated_metadata(func, params)

    return entry.get("description") or description
