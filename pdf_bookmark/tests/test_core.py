from pathlib import Path

import pytest

from pdf_bookmark.core import Heading, analyze_pdf_headings, generate_bookmarks


@pytest.fixture()
def tmp_pdf(tmp_path: Path) -> Path:
    # Create a minimal single-page PDF using pypdf
    from pypdf import PdfWriter

    out = tmp_path / "a.pdf"
    w = PdfWriter()
    w.add_blank_page(width=595, height=842)  # A4
    with out.open("wb") as f:
        w.write(f)
    return out


def test_generate_bookmarks_no_headings(tmp_pdf: Path, tmp_path: Path):
    out = tmp_path / "out.pdf"
    generate_bookmarks(str(tmp_pdf), str(out), [])
    assert out.exists() and out.stat().st_size > 0


def test_generate_bookmarks_with_headings(tmp_pdf: Path, tmp_path: Path):
    out = tmp_path / "out.pdf"
    hs = [Heading(title="Intro", page=1, level=1)]
    generate_bookmarks(str(tmp_pdf), str(out), hs)
    assert out.exists() and out.stat().st_size > 0


def test_analyze_handles_empty_pdf(tmp_pdf: Path):
    # No text, should return empty headings list, not crash
    hs = analyze_pdf_headings(str(tmp_pdf))
    assert isinstance(hs, list)
    assert len(hs) == 0
