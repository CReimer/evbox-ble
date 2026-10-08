"""Prevent relative README links from breaking in the PyPI description."""

import re
import sys
from pathlib import Path


def main() -> None:
    """Require portable HTTPS links or local section anchors."""
    description = Path(sys.argv[1]).read_text()
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", description)
    invalid = [link for link in links if not link.startswith(("https://", "#"))]
    if invalid:
        raise SystemExit(f"README links must work on PyPI: {invalid}")
    print(f"Checked {len(links)} portable README links")


if __name__ == "__main__":
    main()
