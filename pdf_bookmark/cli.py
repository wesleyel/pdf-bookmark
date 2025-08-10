from __future__ import annotations

import argparse
from pathlib import Path

from .core import analyze_pdf_headings, generate_bookmarks


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="pdf-bookmark", description="Auto add bookmarks to PDF")
    p.add_argument("pdf", help="Input PDF path")
    p.add_argument("-o", "--out", help="Output PDF path; default: <name>.bookmarked.pdf")
    p.add_argument("--min-len", type=int, default=3, help="Minimum heading text length")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv)
    src = Path(ns.pdf)
    if not src.exists():
        print(f"File not found: {src}")
        return 2
    out = Path(ns.out) if ns.out else src.with_suffix("")
    if out.suffix.lower() != ".pdf":
        out = Path(str(out) + ".bookmarked.pdf")

    headings = analyze_pdf_headings(str(src), min_len=ns.min_len)
    if not headings:
        print("No headings detected; output will be a copy without outline.")
    generate_bookmarks(str(src), str(out), headings)
    print(f"Wrote: {out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
