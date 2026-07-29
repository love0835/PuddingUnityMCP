"""Tests for PuddingUnityMCP i18n layer (fork additions).

We intentionally do NOT import ``from __future__ import annotations`` because the
i18n layer rewrites ``Annotated`` metadata on real type objects, not on stringified
PEP 563 annotations. Production tool files (Server/src/services/tools/*.py) also
use eager annotations, so this matches reality.
"""
import sys
import types
from typing import Annotated, Literal

import pytest

from transport.translations import (
    apply_translation_to_func,
    get_instructions_for_lang,
    get_translation,
)


def _install_fake_lang(name: str, *, tools=None, instructions=None, groups=None):
    """Inject a fake translation module under transport.translations.<name>."""
    mod_name = f"transport.translations.{name}"
    module = types.ModuleType(mod_name)
    if tools is not None:
        module.TOOL_TRANSLATIONS = tools
    if instructions is not None:
        module.INSTRUCTIONS = instructions
    if groups is not None:
        module.GROUP_TRANSLATIONS = groups
    sys.modules[mod_name] = module
    # Reset the cached loader so the next get_translation call sees the fake.
    from transport import translations as t
    t._LANG_MODULES.pop(name, None)
    return module


def _cleanup_fake_lang(name: str) -> None:
    sys.modules.pop(f"transport.translations.{name}", None)
    from transport import translations as t
    t._LANG_MODULES.pop(name, None)


# ---------------------------------------------------------------------------
# get_translation
# ---------------------------------------------------------------------------


def test_get_translation_en_returns_none():
    assert get_translation("read_console", "en") is None


def test_get_translation_unknown_lang_returns_none():
    assert get_translation("read_console", "fr_FR") is None


def test_get_translation_returns_entry_when_present():
    _install_fake_lang("fake_lang_a", tools={"read_console": {"description": "X"}})
    try:
        assert get_translation("read_console", "fake_lang_a") == {"description": "X"}
        assert get_translation("missing_tool", "fake_lang_a") is None
    finally:
        _cleanup_fake_lang("fake_lang_a")


# ---------------------------------------------------------------------------
# Description override
# ---------------------------------------------------------------------------


def test_apply_translation_overrides_description():
    _install_fake_lang("fake_lang_b", tools={"my_tool": {"description": "中文描述"}})

    async def my_tool():
        pass

    try:
        out = apply_translation_to_func(
            my_tool, "my_tool", "English desc", tool_kwargs={}, lang="fake_lang_b"
        )
        assert out == "中文描述"
    finally:
        _cleanup_fake_lang("fake_lang_b")


def test_apply_translation_en_is_noop_returns_original():
    async def t():
        pass
    assert apply_translation_to_func(t, "t", "EN", tool_kwargs={}, lang="en") == "EN"


def test_apply_translation_unknown_tool_returns_original():
    _install_fake_lang("fake_lang_c", tools={})
    async def t():
        pass
    try:
        assert apply_translation_to_func(t, "t", "EN", tool_kwargs={}, lang="fake_lang_c") == "EN"
    finally:
        _cleanup_fake_lang("fake_lang_c")


# ---------------------------------------------------------------------------
# Annotated metadata rewrite
# ---------------------------------------------------------------------------


def test_annotation_rewrite_plain_annotated():
    _install_fake_lang(
        "fake_lang_d",
        tools={"sample": {"params": {"x": "中文 x 描述"}}},
    )

    async def sample(x: Annotated[int, "english x desc"]) -> None:  # type: ignore[empty-body]
        ...

    try:
        apply_translation_to_func(sample, "sample", None, tool_kwargs={}, lang="fake_lang_d")
        from typing import get_args
        meta = get_args(sample.__annotations__["x"])
        # (type, "metadata", ...)
        assert meta[1] == "中文 x 描述"
    finally:
        _cleanup_fake_lang("fake_lang_d")


def test_annotation_rewrite_inside_union_with_none():
    _install_fake_lang(
        "fake_lang_e",
        tools={"sample": {"params": {"y": "中文 y 描述"}}},
    )

    async def sample(y: Annotated[Literal["a", "b"], "english y desc"] | None = None) -> None:  # type: ignore[empty-body]
        ...

    try:
        apply_translation_to_func(sample, "sample", None, tool_kwargs={}, lang="fake_lang_e")
        # The Annotated arm of the union should now carry the new metadata.
        annot = sample.__annotations__["y"]
        # Walk the union and find the Annotated arm.
        from typing import get_args, get_origin, Annotated as _Annotated
        for arm in get_args(annot):
            if get_origin(arm) is _Annotated or getattr(arm, "__metadata__", None):
                meta = get_args(arm)
                assert meta[1] == "中文 y 描述"
                break
        else:
            pytest.fail("No Annotated arm found in rewritten union")
    finally:
        _cleanup_fake_lang("fake_lang_e")


def test_annotation_rewrite_pydantic_field_metadata():
    """Upstream tools that use Annotated[T, Field(description=...)] must translate too."""
    from pydantic import Field

    _install_fake_lang(
        "fake_lang_field",
        tools={"sample": {"params": {"x": "中文 Field 描述"}}},
    )

    original_field = Field(default="by_name", description="english field desc")

    async def sample(x: Annotated[str, original_field] = "by_name") -> None:  # type: ignore[empty-body]
        ...

    try:
        apply_translation_to_func(sample, "sample", None, tool_kwargs={}, lang="fake_lang_field")
        from typing import get_args
        meta = get_args(sample.__annotations__["x"])
        assert meta[1].description == "中文 Field 描述"
        # The original FieldInfo object must not be mutated (it may be shared).
        assert original_field.description == "english field desc"
        # Non-description Field attributes survive the copy.
        assert meta[1].default == "by_name"
    finally:
        _cleanup_fake_lang("fake_lang_field")


def test_annotation_rewrite_skips_unknown_params():
    _install_fake_lang(
        "fake_lang_f",
        tools={"sample": {"params": {"only_this": "中文"}}},
    )

    async def sample(
        only_this: Annotated[int, "english"],
        not_this: Annotated[int, "untouched"],
    ) -> None:  # type: ignore[empty-body]
        ...

    try:
        apply_translation_to_func(sample, "sample", None, tool_kwargs={}, lang="fake_lang_f")
        from typing import get_args
        assert get_args(sample.__annotations__["only_this"])[1] == "中文"
        assert get_args(sample.__annotations__["not_this"])[1] == "untouched"
    finally:
        _cleanup_fake_lang("fake_lang_f")


# ---------------------------------------------------------------------------
# Title override
# ---------------------------------------------------------------------------


def test_title_override_on_toolannotations():
    _install_fake_lang(
        "fake_lang_g",
        tools={"sample": {"title": "中文標題"}},
    )

    from mcp.types import ToolAnnotations
    annotations_obj = ToolAnnotations(title="English Title")
    tool_kwargs = {"annotations": annotations_obj}

    async def sample():
        pass

    try:
        apply_translation_to_func(sample, "sample", None, tool_kwargs=tool_kwargs, lang="fake_lang_g")
        assert tool_kwargs["annotations"].title == "中文標題"
    finally:
        _cleanup_fake_lang("fake_lang_g")


# ---------------------------------------------------------------------------
# Instructions
# ---------------------------------------------------------------------------


def test_instructions_string_form():
    _install_fake_lang("fake_lang_h", instructions="中文 instructions")
    try:
        assert get_instructions_for_lang("fake_lang_h", True) == "中文 instructions"
        assert get_instructions_for_lang("fake_lang_h", False) == "中文 instructions"
    finally:
        _cleanup_fake_lang("fake_lang_h")


def test_instructions_dict_form_routes_by_project_scoped():
    _install_fake_lang(
        "fake_lang_i",
        instructions={"project_scoped": "scoped 中文", "default": "default 中文"},
    )
    try:
        assert get_instructions_for_lang("fake_lang_i", True) == "scoped 中文"
        assert get_instructions_for_lang("fake_lang_i", False) == "default 中文"
    finally:
        _cleanup_fake_lang("fake_lang_i")


def test_instructions_en_returns_none():
    assert get_instructions_for_lang("en", True) is None


# ---------------------------------------------------------------------------
# Real zh_TW integration smoke test
# ---------------------------------------------------------------------------


def test_zh_TW_module_loads_read_console_from_batch1():
    """Confirms the real zh_TW + _batch1 modules wire up end-to-end."""
    from transport.translations import _LANG_MODULES
    _LANG_MODULES.pop("zh_TW", None)
    entry = get_translation("read_console", "zh_TW")
    assert entry is not None, "read_console missing from zh_TW; _batch1 not loading"
    assert "title" in entry
    assert "params" in entry
    assert "action" in entry["params"]
    # Sanity check: contains Chinese characters
    assert any("一" <= ch <= "鿿" for ch in entry["description"])


def test_zh_TW_module_loads_asset_gen_tools_from_batch5():
    """Confirms the asset_gen tools added in upstream v10.x are translated."""
    from transport.translations import _LANG_MODULES
    _LANG_MODULES.pop("zh_TW", None)
    for tool in ("generate_model", "generate_image", "generate_audio",
                 "import_model", "import_model_file"):
        entry = get_translation(tool, "zh_TW")
        assert entry is not None, f"{tool} missing from zh_TW; _batch5 not loading"
        assert any("一" <= ch <= "鿿" for ch in entry["description"])


def test_zh_TW_covers_all_current_tool_schemas():
    """Every string the extractor finds in tools/ must have a zh_TW counterpart.

    Guards against upstream merges adding tools or params without translations.
    Field(description=...) params are included via the extractor's Field support.
    """
    import sys
    from pathlib import Path

    server_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(server_root / "scripts"))
    try:
        import extract_strings
    finally:
        sys.path.pop(0)

    from transport.translations.zh_TW import TOOL_TRANSLATIONS

    tools_dir = server_root / "src" / "services" / "tools"
    problems = []
    for tool_file in sorted(tools_dir.glob("*.py")):
        if tool_file.name == "__init__.py":
            continue
        for tool_name, entry in extract_strings.extract_from_file(tool_file):
            tr = TOOL_TRANSLATIONS.get(tool_name)
            if tr is None:
                problems.append(f"{tool_name}: no zh_TW entry")
                continue
            for param in entry.get("params", {}):
                if param not in tr.get("params", {}):
                    problems.append(f"{tool_name}.{param}: param untranslated")
    assert not problems, "zh_TW out of sync with tool schemas:\n" + "\n".join(problems)
