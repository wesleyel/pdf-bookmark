from __future__ import annotations

import argparse
from pathlib import Path

from .core import generate_bookmarks, parse_toc_lines


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="pdf-bookmark", description="Auto add bookmarks to PDF")
    p.add_argument("pdf", help="Input PDF path")
    p.add_argument("-o", "--out", help="Output PDF path; default: <name>.bookmarked.pdf")
    p.add_argument("--min-len", type=int, default=3, help="Minimum heading text length")
    p.add_argument("--page-offset", type=int, default=0, help="Page offset: actual - book page")
    p.add_argument("--toc-file", help="Path to a text file containing TOC lines")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv)
    src = Path(ns.pdf)
    if not src.exists():
        print(f"File not found: {src}")
        return 2
    out = Path(ns.out) if ns.out else src.with_suffix(".bookmarked.pdf")

    headings = []
    if ns.toc_file:
        toc_text = Path(ns.toc_file).read_text(encoding="utf-8")
        headings = parse_toc_lines(toc_text, page_offset=ns.page_offset, min_len=ns.min_len)
    else:
        print("No TOC source provided (use --toc-file). Producing a copy without outline.")
        headings = []
    if not headings:
        print("No headings; output will be a copy without outline.")
    generate_bookmarks(str(src), str(out), headings)
    print(f"Wrote: {out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
