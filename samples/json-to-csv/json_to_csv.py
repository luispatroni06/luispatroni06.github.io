#!/usr/bin/env python3
"""Convert a JSON array of flat objects to CSV.

Scope: intended for small, plain JSON files where the top-level value is a list
of dictionaries. Nested values are serialized as compact JSON strings so the CSV
stays valid and reproducible.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any, TextIO


def load_rows(path: Path) -> list[dict[str, Any]]:
    """Load a JSON file and validate the expected top-level shape."""
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError("Input JSON must be an array of objects")

    rows: list[dict[str, Any]] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Item {index} is not an object")
        rows.append(dict(item))
    return rows


def fieldnames_for(rows: Iterable[Mapping[str, Any]]) -> list[str]:
    """Return stable CSV columns: first-seen order across all objects."""
    fields: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                fields.append(key)
                seen.add(key)
    return fields


def cell(value: Any) -> str:
    """Convert one JSON value to a CSV cell string."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (str, int, float)):
        return str(value)
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def write_csv(rows: list[dict[str, Any]], output: TextIO) -> None:
    """Write rows to CSV, filling missing keys with empty strings."""
    fields = fieldnames_for(rows)
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: cell(row.get(field, "")) for field in fields})


def convert(input_path: Path, output_path: Path) -> None:
    rows = load_rows(input_path)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        write_csv(rows, handle)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a JSON array of flat objects to CSV.")
    parser.add_argument("input", type=Path, help="Path to the input .json file")
    parser.add_argument("output", type=Path, help="Path to write the output .csv file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        convert(args.input, args.output)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"error: {exc}") from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
