"""Unit tests for PuddingUnityMCP token saver policy functions (fork additions).

These tests use only the pure functions in transport.token_saver_policies — no
FastMCP, no Unity connection required.
"""
import pytest

from transport.token_saver_policies import (
    VALID_POLICIES,
    apply_policy,
    apply_summary_reference,
    estimate_tokens,
    semantic_compress_text,
    summarize_text,
)


def test_estimate_tokens_is_bytes_over_four():
    assert estimate_tokens(0) == 0
    assert estimate_tokens(3) == 0
    assert estimate_tokens(8) == 2
    assert estimate_tokens(1024) == 256


def test_summarize_keeps_head_and_reports_omitted():
    text = "\n".join(f"line {i}" for i in range(50))
    out = summarize_text(text)
    assert "line 0" in out
    assert "line 11" in out
    assert "line 12" not in out
    assert "[summary] omitted_lines=38" in out


def test_semantic_compression_drops_duplicate_lines():
    text = "\n".join(["repeat"] * 20 + ["unique"])
    out = semantic_compress_text(text)
    assert out.count("repeat") == 1
    assert "unique" in out
    assert "[semantic_compression]" in out


def test_semantic_compression_caps_stacktrace():
    frames = "\n".join(f"  at Frame{i}" for i in range(20))
    out = semantic_compress_text(frames)
    # 6 frames kept, rest omitted
    assert out.count("at Frame") == 6
    assert "[semantic_compression]" in out


def test_apply_policy_passthrough_below_threshold():
    text = "small"
    new_text, transformed = apply_policy(text, "semantic_compression", threshold_tokens=10_000)
    assert new_text == text
    assert transformed is False


def test_apply_policy_raw_never_transforms():
    text = "x" * 10_000
    new_text, transformed = apply_policy(text, "raw", threshold_tokens=10)
    assert new_text == text
    assert transformed is False


def test_apply_policy_unknown_is_passthrough():
    text = "x" * 10_000
    new_text, transformed = apply_policy(text, "garbage", threshold_tokens=10)
    assert new_text == text
    assert transformed is False


def test_apply_policy_semantic_compression_triggers_above_threshold():
    text = "\n".join(f"unique line {i} " + "x" * 50 for i in range(200))
    new_text, transformed = apply_policy(text, "semantic_compression", threshold_tokens=100)
    assert transformed is True
    assert "[semantic_compression]" in new_text
    assert len(new_text) < len(text)


def test_apply_summary_reference_anchors_sha256(tmp_path):
    text = "important payload " * 1000
    out = apply_summary_reference(text, store_dir=tmp_path)
    assert "sha256:" in out
    assert "uri: puddingunitymcp://responses/" in out
    # Original stored on disk
    files = list(tmp_path.glob("*.txt"))
    assert len(files) == 1
    assert files[0].read_text(encoding="utf-8") == text


def test_apply_policy_summary_reference_writes_to_store_dir(tmp_path):
    text = "y" * 20_000
    new_text, transformed = apply_policy(
        text,
        "summary_reference",
        threshold_tokens=100,
        store_dir=tmp_path,
    )
    assert transformed is True
    assert "summary_reference" in new_text
    assert any(tmp_path.glob("*.txt"))


def test_valid_policies_exposes_all_three():
    assert VALID_POLICIES == {"raw", "summary_reference", "semantic_compression"}


# --- Middleware behavioural tests -------------------------------------------------


class _Tool:
    def __init__(self, name: str) -> None:
        self.name = name


class _Content:
    def __init__(self, text: str) -> None:
        self.text = text


class _Result:
    def __init__(self, content):
        self.content = content


@pytest.mark.asyncio
async def test_middleware_on_list_tools_filters_to_whitelist():
    from core.config import config
    from transport.token_saver_middleware import PuddingTokenSaverMiddleware

    config.enabled_tools = ("find_gameobjects", "read_console")
    try:
        mw = PuddingTokenSaverMiddleware()
        all_tools = [_Tool("find_gameobjects"), _Tool("manage_scene"), _Tool("read_console"), _Tool("manage_asset")]

        async def fake_call_next(_ctx):
            return all_tools

        out = await mw.on_list_tools(context=None, call_next=fake_call_next)
        assert sorted(t.name for t in out) == ["find_gameobjects", "read_console"]
    finally:
        config.enabled_tools = None


@pytest.mark.asyncio
async def test_middleware_on_list_tools_passes_through_when_no_whitelist():
    from core.config import config
    from transport.token_saver_middleware import PuddingTokenSaverMiddleware

    config.enabled_tools = None
    mw = PuddingTokenSaverMiddleware()
    all_tools = [_Tool("a"), _Tool("b")]

    async def fake_call_next(_ctx):
        return all_tools

    out = await mw.on_list_tools(context=None, call_next=fake_call_next)
    assert out is all_tools


@pytest.mark.asyncio
async def test_middleware_on_call_tool_compresses_large_text():
    from core.config import config
    from transport.token_saver_middleware import PuddingTokenSaverMiddleware

    config.response_policy = "semantic_compression"
    config.response_threshold_tokens = 100
    try:
        mw = PuddingTokenSaverMiddleware()
        big_text = "\n".join(f"line {i} " + "x" * 50 for i in range(500))
        content = [_Content(big_text)]
        result = _Result(content)

        async def fake_call_next(_ctx):
            return result

        out = await mw.on_call_tool(context=None, call_next=fake_call_next)
        assert out is result
        assert len(content[0].text) < len(big_text)
        assert "[semantic_compression]" in content[0].text
    finally:
        config.response_policy = "raw"
        config.response_threshold_tokens = 1200


@pytest.mark.asyncio
async def test_middleware_on_call_tool_raw_passes_through():
    from core.config import config
    from transport.token_saver_middleware import PuddingTokenSaverMiddleware

    config.response_policy = "raw"
    mw = PuddingTokenSaverMiddleware()
    original = "x" * 100_000
    content = [_Content(original)]
    result = _Result(content)

    async def fake_call_next(_ctx):
        return result

    out = await mw.on_call_tool(context=None, call_next=fake_call_next)
    assert out is result
    assert content[0].text == original
