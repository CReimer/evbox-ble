"""Require complete line and branch coverage without percentage rounding."""

import json
import sys
from pathlib import Path


def main() -> None:
    """Reject incomplete or empty coverage reports."""
    totals = json.loads(Path(sys.argv[1]).read_text())["totals"]
    if (
        not totals["num_statements"]
        or not totals["num_branches"]
        or totals["missing_lines"]
        or totals["missing_branches"]
    ):
        raise SystemExit(
            "Library requires 100% line and branch coverage, with neither count empty"
        )
    print(
        f"Lines: {totals['covered_lines']}/{totals['num_statements']}; branches: {totals['covered_branches']}/{totals['num_branches']}"
    )


if __name__ == "__main__":
    main()
