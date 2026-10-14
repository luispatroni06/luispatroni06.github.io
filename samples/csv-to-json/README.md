# CSV to JSON sample

Small self-contained Python utility prepared as proof for OpenTask-style data conversion work.

## Scope

- Input: a local CSV file with a header row.
- Output: a JSON array of objects, one object per CSV row.
- Delimiters: attempts to sniff comma, semicolon, tab, and pipe; supports an explicit `--delimiter` override.
- Formatting: pretty JSON by default, compact JSON with `--compact`.
- Error handling: missing headers, empty header names, and rows with extra fields produce clear errors.

Out of scope: streaming very large files, private systems, credentials, APIs, scraping, or arbitrary client code execution.

## Run

```bash
python3 csv_to_json.py sample.csv sample.json
python3 csv_to_json.py sample-semicolon.csv sample.json --delimiter ';' --compact
```

## Test

The tests use `unittest` so they can run without installing dependencies:

```bash
python3 -m unittest -v
```

They cover delimiter sniffing, delimiter override, quoted commas/newlines, invalid row shape, JSON formatting, and end-to-end conversion.
