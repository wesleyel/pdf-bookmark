from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextBoxHorizontal, LTChar
from pypdf import PdfReader, PdfWriter


@dataclass
class Heading:
    title: str
    page: int  # 1-based
    level: int  # 1..6


def _iter_text_boxes(layout) -> Iterable[LTTextBoxHorizontal]:
    for element in layout:
        if isinstance(element, LTTextBoxHorizontal):
            yield element
        # pdfminer can nest containers; recurse if needed (rare for text boxes)
        if isinstance(element, LTTextContainer):
            for child in getattr(element, "_objs", []):
                if isinstance(child, LTTextBoxHorizontal):
                    yield child


def analyze_pdf_headings(pdf_path: str, min_len: int = 3) -> List[Heading]:
    """
    Heuristically detect headings by font size and position.
    - Larger average character size => higher-level heading
    - Near top region of page boosts confidence
    - Single-line and short text favored
    Returns a sorted list of Heading(title, page, level)
    """
    headings: List[Heading] = []

    sizes: List[float] = []
    candidates: List[Tuple[int, str, float, float]] = []  # (page, text, avg_size, y_top)

    for page_no, layout in enumerate(extract_pages(pdf_path), start=1):
        for box in _iter_text_boxes(layout):
            text = box.get_text().strip()
            if not text:
                continue
            # keep a single line representative
            first_line = text.splitlines()[0].strip()
            if len(first_line) < min_len:
                continue

            char_sizes: List[float] = []
            for obj in getattr(box, "_objs", []):
                if hasattr(obj, "_objs"):
                    for ch in getattr(obj, "_objs", []):
                        if isinstance(ch, LTChar):
                            char_sizes.append(ch.size)
                elif isinstance(obj, LTChar):
                    char_sizes.append(obj.size)

            if not char_sizes:
                continue
            avg_size = sum(char_sizes) / len(char_sizes)
            sizes.append(avg_size)
            y0, y1 = box.y0, box.y1
            candidates.append((page_no, first_line, avg_size, y1))

    if not candidates:
        return []

    # Determine thresholds by quantiles
    sizes_sorted = sorted(sizes)
    def quantile(q: float) -> float:
        idx = int(q * (len(sizes_sorted) - 1))
        return sizes_sorted[idx]

    q70, q85 = quantile(0.70), quantile(0.85)

    # Compute levels: 1 if > q85, 2 if > q70, else 3 (cap to 6 later if needed)
    for page, text, avg_size, y_top in candidates:
        base_level = 1 if avg_size >= q85 else (2 if avg_size >= q70 else 3)
        # boost if close to top of page
        top_boost = -1 if y_top > 700 else 0  # typical A4 height ~ 842
        level = max(1, min(6, base_level + top_boost))
        headings.append(Heading(title=text, page=page, level=level))

    # Sort by page then by level
    headings.sort(key=lambda h: (h.page, h.level, h.title.lower()))
    return headings


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
