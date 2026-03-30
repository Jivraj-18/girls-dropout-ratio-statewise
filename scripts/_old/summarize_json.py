from __future__ import annotations

import json
import sys


def main() -> None:
    obj = json.load(sys.stdin)

    print("top_type:", type(obj).__name__)
    if isinstance(obj, dict):
        print("top_keys:", list(obj.keys())[:25])
        items = (
            obj.get("data")
            if obj.get("data") is not None
            else obj.get("result")
            if obj.get("result") is not None
            else obj.get("rows")
        )
    else:
        items = obj

    print("items_type:", type(items).__name__)
    if isinstance(items, list):
        print("items_len:", len(items))
        if items:
            first = items[0]
            print("item0_type:", type(first).__name__)
            if isinstance(first, dict):
                keys = list(first.keys())
                print("item0_keys:", keys[:25])
                preview = {k: first[k] for k in keys[:8]}
                print("item0_preview:", preview)
            else:
                print("item0_preview:", first)


if __name__ == "__main__":
    main()
