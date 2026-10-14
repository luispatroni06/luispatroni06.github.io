import io
import json
import tempfile
import unittest
from pathlib import Path

from csv_to_json import convert, read_csv_rows, write_json


class CsvToJsonTests(unittest.TestCase):
    def test_reads_comma_csv_as_objects(self):
        rows = read_csv_rows(io.StringIO("name,email\nAda,ada@example.com\nGrace,grace@example.com\n"))
        self.assertEqual(rows, [
            {"name": "Ada", "email": "ada@example.com"},
            {"name": "Grace", "email": "grace@example.com"},
        ])

    def test_sniffs_semicolon_delimiter(self):
        rows = read_csv_rows(io.StringIO("name;role\nAda;engineer\n"))
        self.assertEqual(rows[0], {"name": "Ada", "role": "engineer"})

    def test_explicit_delimiter_override(self):
        rows = read_csv_rows(io.StringIO("name|score\nAda|10\n"), delimiter="|")
        self.assertEqual(rows[0], {"name": "Ada", "score": "10"})

    def test_preserves_quoted_commas_and_newlines(self):
        rows = read_csv_rows(io.StringIO('name,note\nAda,"hello, world"\nGrace,"line 1\nline 2"\n'))
        self.assertEqual(rows[0]["note"], "hello, world")
        self.assertEqual(rows[1]["note"], "line 1\nline 2")

    def test_rejects_rows_with_extra_values(self):
        with self.assertRaisesRegex(ValueError, "more values than headers"):
            read_csv_rows(io.StringIO("name,email\nAda,ada@example.com,extra\n"))

    def test_write_json_compact_and_pretty(self):
        pretty = io.StringIO()
        compact = io.StringIO()
        rows = [{"name": "Ada"}]
        write_json(rows, pretty, pretty=True)
        write_json(rows, compact, pretty=False)
        self.assertIn("\n  {", pretty.getvalue())
        self.assertEqual(compact.getvalue(), '[{"name":"Ada"}]\n')

    def test_convert_writes_expected_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.csv"
            output_path = Path(tmpdir) / "output.json"
            input_path.write_text("name,email\nAda,ada@example.com\n", encoding="utf-8")
            convert(input_path, output_path)
            self.assertEqual(json.loads(output_path.read_text(encoding="utf-8")), [{"name": "Ada", "email": "ada@example.com"}])


if __name__ == "__main__":
    unittest.main()
