"""Extract translatable schema strings from tool files into JSON.

Run: python scripts/extract_strings.py <tool_file_basename> [more...]
Writes JSON to stdout. Each tool entry contains description, title, params (Annotated).
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent / "src" / "services" / "tools"


def _str_from(node):
    """Return string value if node is a Constant string; else None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    # Concatenation (string + string) — try to evaluate
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _str_from(node.left)
        right = _str_from(node.right)
        if left is not None and right is not None:
            return left + right
    # Tuple wrapped string (parenthesized multi-line string)
    if isinstance(node, ast.Tuple) and len(node.elts) == 1:
        return _str_from(node.elts[0])
    return None


def _extract_annotated_desc(annotation):
    """Return the first string metadata inside Annotated[...] or union arms; else None."""
    if annotation is None:
        return None

    # Annotated[T, "desc", ...] -> Subscript with value Name("Annotated") and slice Tuple
    if isinstance(annotation, ast.Subscript):
        value = annotation.value
        if isinstance(value, ast.Name) and value.id == "Annotated":
            slice_node = annotation.slice
            if isinstance(slice_node, ast.Tuple) and len(slice_node.elts) >= 2:
                for elt in slice_node.elts[1:]:
                    s = _str_from(elt)
                    if s is not None:
                        return s
        # Subscript on other types — could be Optional[Annotated[...]] etc., recurse
        return _extract_annotated_desc(annotation.value)

    # Union via PEP 604 (X | Y) — BinOp with BitOr
    if isinstance(annotation, ast.BinOp) and isinstance(annotation.op, ast.BitOr):
        for sub in (annotation.left, annotation.right):
            s = _extract_annotated_desc(sub)
            if s is not None:
                return s

    return None


def extract_from_file(path: Path):
    """Return list of tool entries found in this file."""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    entries = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        # Find @mcp_for_unity_tool decorator
        decorator = None
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call):
                func = dec.func
                func_name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
                if func_name == "mcp_for_unity_tool":
                    decorator = dec
                    break
        if decorator is None:
            continue

        # Read decorator kwargs
        description = None
        tool_name = node.name
        title = None
        for kw in decorator.keywords:
            if kw.arg == "description":
                description = _str_from(kw.value)
            elif kw.arg == "name":
                n = _str_from(kw.value)
                if n:
                    tool_name = n
            elif kw.arg == "annotations":
                # ToolAnnotations(title="...")
                if isinstance(kw.value, ast.Call):
                    for sub_kw in kw.value.keywords:
                        if sub_kw.arg == "title":
                            title = _str_from(sub_kw.value)

        # Extract Annotated params from function signature
        params = {}
        args = node.args
        for arg in args.args + args.kwonlyargs:
            if arg.arg == "ctx":
                continue
            desc = _extract_annotated_desc(arg.annotation)
            if desc is not None:
                params[arg.arg] = desc

        entry = {}
        if description:
            entry["description"] = description
        if title:
            entry["title"] = title
        if params:
            entry["params"] = params
        if entry:
            entries.append((tool_name, entry))

    return entries


def main(argv):
    if len(argv) < 3:
        print("usage: extract_strings.py <output_path> <file_basename> [more...]", file=sys.stderr)
        sys.exit(2)

    output_path = Path(argv[1])
    out = {}
    for name in argv[2:]:
        path = TOOLS_DIR / name
        if not path.exists():
            print(f"# skip missing: {name}", file=sys.stderr)
            continue
        try:
            for tool_name, entry in extract_from_file(path):
                out[tool_name] = entry
        except Exception as exc:
            print(f"# error in {name}: {exc}", file=sys.stderr)

    output_path.write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"wrote {output_path}: {len(out)} tools", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv)
