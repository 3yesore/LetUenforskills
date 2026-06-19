"""Export the bundled multi-skill demo into the local static site."""

from __future__ import annotations

import argparse
from pathlib import Path

from asa.report_exporter import export_report


DEFAULT_RUN = Path("runs/demo-multi-skill")
DEFAULT_OUTPUT = Path("site/report")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the bundled multi-skill demo report and cinema manifest.")
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN, help="Run directory to export. Defaults to runs/demo-multi-skill.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Report output directory. Defaults to site/report.")
    args = parser.parse_args()

    result = export_report(args.run, args.output)
    print(f"Exported demo report: {result['index']}")
    print(f"Skill pages: {result['skill_count']}")
    print("Cinema manifest: site/cinema/cinema-data.json")
    print("Serve locally: python -m http.server 4173 -d site")
    print("Open: http://localhost:4173/cinema/")


if __name__ == "__main__":
    main()
