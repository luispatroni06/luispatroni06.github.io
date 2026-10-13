import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from json_to_csv import cell, convert, fieldnames_for, load_rows, write_csv


class JsonToCsvTests(unittest.TestCase):
    def test_fieldnames_use_first_seen_order_across_rows(self):
        rows = [{"name": "Ada", "email": "ada@example.com"}, {"role": "engineer", "name": "Grace"}]
        self.assertEqual(fieldnames_for(rows), ["name", "email", "role"])

    def test_missing_keys_become_empty_cells(self):
        output = io.StringIO()
        write_csv([{"name": "Ada", "email": "ada@example.com"}, {"name": "Grace"}], output)
        parsed = list(csv.DictReader(io.StringIO(output.getvalue())))
        self.assertEqual(parsed[1]["email"], "")

    def test_csv_escaping_quotes_commas_and_newlines(self):
        output = io.StringIO()
        write_csv([{"note": "hello, \"Ada\"\nnext line"}], output)
        parsed = list(csv.DictReader(io.StringIO(output.getvalue())))
        self.assertEqual(parsed[0]["note"], "hello, \"Ada\"\nnext line")

    def test_json_value_cells_are_stable(self):
        self.assertEqual(cell(True), "true")
        self.assertEqual(cell(False), "false")
        self.assertEqual(cell(None), "")
        self.assertEqual(cell(["a", 2]), '["a",2]')

    def test_load_rows_rejects_non_array(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "input.json"
            path.write_text('{"name":"Ada"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "array of objects"):
                load_rows(path)

    def test_convert_writes_expected_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.json"
            output_path = Path(tmpdir) / "output.csv"
            input_path.write_text(
                json.dumps([
                    {"name": "Ada", "score": 10},
                    {"name": "Grace", "email": "grace@example.com"},
                ]),
                encoding="utf-8",
            )
            convert(input_path, output_path)
            parsed = list(csv.DictReader(io.StringIO(output_path.read_text(encoding="utf-8"))))
            self.assertEqual(parsed[0], {"name": "Ada", "score": "10", "email": ""})
            self.assertEqual(parsed[1], {"name": "Grace", "score": "", "email": "grace@example.com"})


if __name__ == "__main__":
    unittest.main()
