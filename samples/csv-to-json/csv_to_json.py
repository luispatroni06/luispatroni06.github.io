#!/usr/bin/env python3
"""Convert CSV files to JSON arrays of objects.

Scope: intended for small local CSV files. It can sniff common delimiters,
accept an explicit delimiter, and emit either pretty or compact JSON.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import TextIO


COMMON_DELIMITERS = [",", ";", "\t", "|"]


def sniff_dialect(sample: str, fallback_delimiter: str = ",") -> type[csv.Dialect]:
    """Detect a CSV dialect class from a text sample, falling back safely."""
    try:
        return csv.Sniffer().sniff(sample, delimiters="".join(COMMON_DELIMITERS))
    except csv.Error:
        class Fallback(csv.excel):
            delimiter = fallback_delimiter
            lineterminator = "\n"
        return Fallback


def read_csv_rows(input_file: TextIO, delimiter: str | None = None) -> list[dict[str, str]]:
    """Read CSV rows as dictionaries, validating headers and row shape."""
    sample = input_file.read(4096)
    input_file.seek(0)
    dialect = sniff_dialect(sample, delimiter or ",")
    if delimiter is not None:
        dialect.delimiter = delimiter

    reader = csv.DictReader(input_file, dialect=dialect)
    if not reader.fieldnames:
        raise ValueError("CSV input must include a header row")

    if any(name is None or name == "" for name in reader.fieldnames):
        raise ValueError("CSV header names must not be empty")

    rows: list[dict[str, str]] = []
    for line_number, row in enumerate(reader, start=2):
        if None in row:
            raise ValueError(f"Row {line_number} has more values than headers")
        rows.append({key: (value if value is not None else "") for key, value in row.items()})
    return rows


def write_json(rows: list[dict[str, str]], output_file: TextIO, pretty: bool = True) -> None:
    """Write rows as a JSON array."""
    if pretty:
        json.dump(rows, output_file, ensure_ascii=False, indent=2)
    else:
        json.dump(rows, output_file, ensure_ascii=False, separators=(",", ":"))
    output_file.write("\n")


def convert(input_path: Path, output_path: Path, delimiter: str | None = None, compact: bool = False) -> None:
    with input_path.open("r", encoding="utf-8", newline="") as input_file:
        rows = read_csv_rows(input_file, delimiter=delimiter)
    with output_path.open("w", encoding="utf-8") as output_file:
        write_json(rows, output_file, pretty=not compact)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a CSV file to a JSON array of objects.")
    parser.add_argument("input", type=Path, help="Path to the input .csv file")
    parser.add_argument("output", type=Path, help="Path to write the output .json file")
    parser.add_argument("--delimiter", help="Optional delimiter override, e.g. ';' or '|'", default=None)
    parser.add_argument("--compact", action="store_true", help="Write compact JSON instead of indented JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.delimiter is not None and len(args.delimiter) != 1:
        raise SystemExit("error: --delimiter must be exactly one character")
    try:
        convert(args.input, args.output, delimiter=args.delimiter, compact=args.compact)
    except (OSError, UnicodeDecodeError, csv.Error, ValueError) as exc:
        raise SystemExit(f"error: {exc}") from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
