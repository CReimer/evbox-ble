"""Verify that CI rejects coverage gaps and empty reports."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CoverageGateTests(unittest.TestCase):
    def test_complete_report_passes(self) -> None:
        self.assertEqual(self.run_gate(0, 0, 10, 4), 0)

    def test_gaps_or_empty_reports_fail(self) -> None:
        for counts in [(1, 0, 10, 4), (0, 1, 10, 4), (0, 0, 0, 4), (0, 0, 10, 0)]:
            with self.subTest(counts=counts):
                self.assertNotEqual(self.run_gate(*counts), 0)

    def run_gate(
        self, missing_lines: int, missing_branches: int, lines: int, branches: int
    ) -> int:
        with tempfile.TemporaryDirectory() as folder:
            report = Path(folder) / "coverage.json"
            report.write_text(
                json.dumps(
                    {
                        "totals": {
                            "num_statements": lines,
                            "num_branches": branches,
                            "missing_lines": missing_lines,
                            "missing_branches": missing_branches,
                            "covered_lines": lines - missing_lines,
                            "covered_branches": branches - missing_branches,
                        }
                    }
                )
            )
            return subprocess.run(
                [
                    sys.executable,
                    str(
                        Path(__file__).resolve().parents[1] / "tools/check_coverage.py"
                    ),
                    str(report),
                ],
                capture_output=True,
                check=False,
            ).returncode
