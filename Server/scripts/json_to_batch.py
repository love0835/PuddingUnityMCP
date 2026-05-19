"""Convert translated JSON to _batchN.py Python module.

Usage: python scripts/json_to_batch.py <batch_num> <translated.json> > _batchN.py
"""
from __future__ import annotations

import json
import sys


def main() -> None:
    if len(sys.argv) != 4:
        print("usage: json_to_batch.py <batch_num> <translated_json_path> <output_py_path>", file=sys.stderr)
        sys.exit(2)
    batch_num = int(sys.argv[1])
    data = json.loads(open(sys.argv[2], encoding="utf-8").read())

    parts = [
        f'"""Batch {batch_num} zh_TW translations (auto-generated; merged into zh_TW.py)."""',
        '',
        f"BATCH_{batch_num} = {json.dumps(data, ensure_ascii=False, indent=4)}",
        '',
    ]
    open(sys.argv[3], 'w', encoding='utf-8').write("\n".join(parts))
    print(f"wrote {sys.argv[3]}: BATCH_{batch_num} with {len(data)} tools", file=sys.stderr)


if __name__ == "__main__":
    main()
