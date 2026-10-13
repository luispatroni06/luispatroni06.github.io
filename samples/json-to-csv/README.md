# JSON array to CSV sample

Small self-contained Python utility prepared as proof for OpenTask-style data conversion work.

## Scope

- Input: a JSON file whose top-level value is an array of objects.
- Output: a CSV file.
- Column order: first time each key appears across the array.
- Missing keys: empty cells.
- CSV escaping: handled by Python's standard `csv` module.
- Nested arrays/objects: serialized as compact JSON strings.

Out of scope: streaming very large files, private systems, credentials, APIs, scraping, or arbitrary client code execution.

## Run

```bash
python3 json_to_csv.py sample.json sample.csv
```

## Test

The tests are written with `unittest` so they can also run in minimal environments:

```bash
python3 -m unittest -v
```

They cover first-seen column ordering, missing-key blanks, CSV escaping, value conversion, invalid input shape, and end-to-end conversion.
