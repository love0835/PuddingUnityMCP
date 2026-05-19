"""
Token saver response transformation policies.

Pure functions ported from MCPzip recorder.py. No FastMCP dependencies, easy to unit test.

Three policies are available:

- ``raw``: pass response through unchanged.
- ``summary_reference``: replace large response text with a short summary + sha256 + URI.
  The original text is optionally written to ``store_dir`` so it can be retrieved out-of-band.
- ``semantic_compression``: deduplicate lines, cap stack-trace depth, truncate at a char limit.
  No artifacts are written; the compressed text is returned inline.

Token estimation uses ``bytes / 4`` to stay framework-agnostic; this matches MCPzip's
estimator so absolute numbers are comparable across the two codebases.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

VALID_POLICIES = {"raw", "summary_reference", "semantic_compression"}


def estimate_tokens(byte_len: int) -> int:
    """Rough token estimate: bytes / 4. Matches MCPzip recorder estimator."""
    return max(0, byte_len // 4)


def summarize_text(text: str, limit: int = 900) -> str:
    """Return a short head-of-text summary plus an [summary] tag with omitted-line count."""
    lines = [line.rstrip() for line in text.splitlines()]
    non_empty = [line for line in lines if line.strip()]
    head = "\n".join(non_empty[:12])
    if len(head) > limit:
        head = head[:limit] + "\n..."
    omitted = max(0, len(non_empty) - 12)
    return f"{head}\n\n[summary] omitted_lines={omitted}, original_chars={len(text)}"


def semantic_compress_text(text: str, limit: int = 2400) -> str:
    """Deduplicate normalized lines, cap stack traces at 6 frames, truncate at ``limit`` chars."""
    lines = [line.rstrip() for line in text.splitlines()]
    kept: list[str] = []
    seen: set[str] = set()
    stack_lines = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        normalized = re.sub(r"\s+", " ", stripped)
        looks_stack = (
            normalized.startswith("at ")
            or normalized.startswith("File ")
            or "traceback" in normalized.lower()
            or re.search(r":line\s+\d+", normalized, flags=re.I) is not None
        )
        if looks_stack:
            stack_lines += 1
            if stack_lines > 6:
                continue
        key = normalized[:180]
        if key in seen:
            continue
        seen.add(key)
        kept.append(stripped)
        if sum(len(x) + 1 for x in kept) >= limit:
            break

    compressed = "\n".join(kept)
    omitted = max(0, len(lines) - len(kept))
    if len(compressed) > limit:
        compressed = compressed[:limit] + "\n..."
    return f"{compressed}\n\n[semantic_compression] omitted_lines={omitted}, original_chars={len(text)}"


def apply_summary_reference(text: str, store_dir: Path | None = None) -> str:
    """Replace ``text`` with sha256-anchored summary; optionally persist original to ``store_dir``."""
    digest = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
    uri = f"puddingunitymcp://responses/{digest}.txt"
    if store_dir is not None:
        try:
            store_dir.mkdir(parents=True, exist_ok=True)
            (store_dir / f"{digest}.txt").write_text(text, encoding="utf-8")
        except OSError:
            pass
    return (
        "[PuddingUnityMCP summary_reference]\n"
        f"uri: {uri}\n"
        f"sha256: {digest}\n"
        f"original_chars: {len(text)}\n"
        f"original_tokens_est: {estimate_tokens(len(text.encode('utf-8', errors='replace')))}\n\n"
        f"{summarize_text(text)}"
    )


def apply_policy(
    text: str,
    policy: str,
    threshold_tokens: int,
    store_dir: Path | None = None,
) -> tuple[str, bool]:
    """Apply ``policy`` to ``text`` when its estimated tokens exceed ``threshold_tokens``.

    Returns ``(new_text, transformed)``. When ``transformed`` is False the original text
    is returned unchanged (either because the policy is raw, the threshold was not hit,
    or the policy is unrecognized).
    """
    if policy == "raw" or policy not in VALID_POLICIES:
        return text, False
    if estimate_tokens(len(text.encode("utf-8", errors="replace"))) < threshold_tokens:
        return text, False
    if policy == "summary_reference":
        return apply_summary_reference(text, store_dir=store_dir), True
    if policy == "semantic_compression":
        return semantic_compress_text(text), True
    return text, False
