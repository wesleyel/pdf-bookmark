from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, List, Tuple, Optional

from pypdf import PdfReader, PdfWriter


@dataclass
class Heading:
    title: str
    page: int  # 1-based
    level: int  # 1..6


def generate_bookmarks(src_pdf: str, out_pdf: str, headings: Iterable[Heading]) -> None:
    """Write given headings into a new PDF file as outline/bookmarks."""
    reader = PdfReader(src_pdf)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    # Build hierarchical outlines using a simple stack by levels
    stack: List[Tuple[int, object]] = []  # (level, parent_ref)

    for h in headings:
        page_index = max(0, min(len(reader.pages) - 1, h.page - 1))
        while stack and stack[-1][0] >= h.level:
            stack.pop()
        parent = stack[-1][1] if stack else None
        dest = writer.add_outline_item(h.title, page_index, parent=parent)
        stack.append((h.level, dest))

    with open(out_pdf, "wb") as f:
        writer.write(f)


# -------------------- TOC parsing utilities --------------------

_NUM_PREFIX_RE = re.compile(
    r"^\s*(?P<num>(第\s*\d+[一二三四五六七八九十百千]*[章节节部分编]?)|((\d+\.)+\d+)|\d+)?\s*"
)
_TRAILING_PAGE_RE = re.compile(r"(?P<page>\d{1,5})\s*$")


def _infer_level_from_numbering(num: Optional[str]) -> int:
    if not num:
        return 1
    num = num.strip()
    if num.startswith("第"):
        # "第1章" style => top-level
        return 1
    if "." in num:
        # "1.2.3" => level = segments + 1 (so 1.2 is level 2)
        return min(6, max(1, num.count(".") + 1))
    # Simple leading integer like "1" => level 1
    return 1


def parse_toc_lines(toc_text: str, page_offset: int = 0, min_len: int = 1) -> List[Heading]:
    """
    Parse a pasted TOC text into Heading entries.
    - Each line should end with the book page number (digits)
    - Leading numbering like "第1章" or "1.2" is used to infer the level
    - page_offset is added to the parsed page number to map to PDF actual pages
    """
    headings: List[Heading] = []
    for raw_line in toc_text.splitlines():
        line = raw_line.strip()
        if len(line) < min_len:
            continue
        # Detect and temporarily strip leading asterisk marker(s)
        star_prefix = ""
        m_star = re.match(r"^\*+\s*", line)
        if m_star:
            stars = m_star.group(0)
            star_count = stars.count("*")
            # Preserve star(s) without trailing space; spacing will be normalized later
            star_prefix = ("*" * star_count)
            line = line[m_star.end() :].lstrip()

        # Extract trailing page digits
        page_m = _TRAILING_PAGE_RE.search(line)
        if not page_m:
            continue
        page_num = int(page_m.group("page"))
        # Remove trailing page from the line
        line_wo_page = line[: page_m.start()].rstrip()
        # Extract leading numbering if exists
        num_m = _NUM_PREFIX_RE.match(line_wo_page)
        numbering = None
        title_part = line_wo_page
        if num_m:
            numbering = num_m.group("num")
            title_part = line_wo_page[num_m.end() :].strip()
        # Build title while preserving numbering prefix (e.g., "第1章" or "1.1")
        if numbering:
            combined = f"{numbering.strip()} {title_part}".strip()
        else:
            combined = title_part
        # Cleanup whitespace
        title = re.sub(r"\s+", " ", combined)
        if not title:
            # fallback to raw without numbering
            title = line_wo_page.strip()
        # Restore asterisk prefix if present
        if star_prefix:
            # No space between star(s) and numbering/title
            title = f"{star_prefix}{title}".strip()
        level = _infer_level_from_numbering(numbering)
        pdf_page = max(1, page_num + page_offset)
        headings.append(Heading(title=title, page=pdf_page, level=level))

    # Sort by page then by inferred level
    headings.sort(key=lambda h: (h.page, h.level, h.title.lower()))
    return headings


## URL/website TOC fetching intentionally removed; only manual text input is supported.


