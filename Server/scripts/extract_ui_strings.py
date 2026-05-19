"""Extract UI strings from MCPForUnity (UXML + C# hardcoded UI text) to JSON.

Run: python scripts/extract_ui_strings.py <output_json_path>

Pulls:
- UXML: text="...", placeholder-text="..." attributes
- C#:   .tooltip = "..."; .text = "..."; EditorUtility.DisplayDialog("title", "body", "btn")
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

UI_ROOT = Path(__file__).resolve().parent.parent.parent / "MCPForUnity" / "Editor"

UXML_TEXT_RE = re.compile(r'\b(?:text|placeholder-text)="([^"]+)"')
CS_TOOLTIP_RE = re.compile(r'\.tooltip\s*=\s*"((?:[^"\\]|\\.)*)"')
CS_TEXT_ASSIGN_RE = re.compile(r'\.text\s*=\s*"((?:[^"\\]|\\.)*)"')
CS_DISPLAY_DIALOG_RE = re.compile(
    r'EditorUtility\.DisplayDialog\(\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"',
    re.MULTILINE,
)
CS_LABEL_NEW_RE = re.compile(r'new\s+(?:Label|Button|Foldout)\s*\(\s*"((?:[^"\\]|\\.)*)"')


def is_translatable(s: str) -> bool:
    s = s.strip()
    if not s or len(s) < 2:
        return False
    # Skip if all symbols/digits
    if not any(c.isalpha() for c in s):
        return False
    # Skip URLs and paths
    if s.startswith(("http://", "https://", "/", "Assets/")):
        return False
    # Skip identifiers (CamelCase no space)
    if " " not in s and "_" in s and any(c == "_" for c in s):
        return False
    return True


def walk():
    strings: dict[str, list[str]] = {}

    def add(text: str, source: str) -> None:
        text = text.strip()
        if not is_translatable(text):
            return
        # Unescape simple C# escapes
        text = text.replace('\\"', '"').replace("\\n", "\n").replace("\\t", "\t")
        if text not in strings:
            strings[text] = []
        if source not in strings[text]:
            strings[text].append(source)

    for path in UI_ROOT.rglob("*.uxml"):
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(UI_ROOT).as_posix()
        for m in UXML_TEXT_RE.finditer(content):
            add(m.group(1), rel)

    for path in UI_ROOT.rglob("*.cs"):
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(UI_ROOT).as_posix()
        for m in CS_TOOLTIP_RE.finditer(content):
            add(m.group(1), rel)
        for m in CS_TEXT_ASSIGN_RE.finditer(content):
            add(m.group(1), rel)
        for m in CS_LABEL_NEW_RE.finditer(content):
            add(m.group(1), rel)
        for m in CS_DISPLAY_DIALOG_RE.finditer(content):
            add(m.group(1), rel)
            add(m.group(2), rel)

    return strings


def main():
    if len(sys.argv) != 2:
        print("usage: extract_ui_strings.py <output_json>", file=sys.stderr)
        sys.exit(2)
    strings = walk()
    # Sort by english text for stable output
    ordered = dict(sorted(strings.items()))
    out_path = Path(sys.argv[1])
    out_path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path}: {len(ordered)} unique strings", file=sys.stderr)


if __name__ == "__main__":
    main()
