#!/usr/bin/env python3
"""Generic PDF page extractor for tech blog writing.

Extracts specified pages from a PDF file as high-resolution PNG images.
Uses PyMuPDF (fitz) which has no external system dependencies.

Author: Damon Li

Usage:
    # Extract specific pages (1-indexed)
    python extract_pdf_pages.py report.pdf --pages 1 2 4 7 --output ./images

    # Extract specific pages with custom filenames
    python extract_pdf_pages.py report.pdf --output ./images --mapping '{
        "1": "cover",
        "2": "table_of_contents",
        "5": "architecture_diagram"
    }'

    # Extract all pages
    python extract_pdf_pages.py report.pdf --all --output ./images

    # Adjust quality (zoom factor, default 2.0)
    python extract_pdf_pages.py report.pdf --pages 1 --zoom 3.0 --output ./images

Dependencies:
    pip install PyMuPDF
"""

import argparse
import json
import os
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF is not installed. Run: pip install PyMuPDF")
    sys.exit(1)


def extract_pages(
    pdf_path: str,
    output_dir: str,
    page_mapping: dict[int, str] | None = None,
    pages: list[int] | None = None,
    extract_all: bool = False,
    zoom: float = 2.0,
    prefix: str = "",
) -> list[dict]:
    """Extract pages from a PDF as PNG images.

    Args:
        pdf_path: Path to the source PDF file.
        output_dir: Directory to save extracted images.
        page_mapping: Dict mapping 1-indexed page numbers to custom filenames.
        pages: List of 1-indexed page numbers to extract.
        extract_all: If True, extract all pages.
        zoom: Zoom factor for rendering quality (2.0 = 2x resolution).
        prefix: Optional prefix for output filenames.

    Returns:
        List of result dicts with 'page', 'path', 'status' keys.
    """
    os.makedirs(output_dir, exist_ok=True)
    results: list[dict] = []

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"PDF: {pdf_path} ({total_pages} pages)")

    # Determine which pages to extract
    if page_mapping:
        targets = {int(k): v for k, v in page_mapping.items()}
    elif pages:
        targets = {p: f"{prefix}page{p:02d}" for p in pages}
    elif extract_all:
        targets = {p: f"{prefix}page{p:02d}" for p in range(1, total_pages + 1)}
    else:
        print("Error: specify --pages, --mapping, or --all.")
        doc.close()
        sys.exit(1)

    mat = fitz.Matrix(zoom, zoom)

    for page_num, filename in sorted(targets.items()):
        if page_num < 1 or page_num > total_pages:
            print(f"  SKIP page {page_num} (out of range 1-{total_pages})")
            results.append({"page": page_num, "path": "N/A", "status": "SKIPPED"})
            continue

        page = doc[page_num - 1]
        pix = page.get_pixmap(matrix=mat)
        out_path = os.path.join(output_dir, f"{filename}.png")
        pix.save(out_path)
        size = os.path.getsize(out_path)

        print(f"  Page {page_num:3d} -> {out_path} ({size / 1024:.1f} KB)")
        results.append({"page": page_num, "path": out_path, "status": "SUCCESS", "size": size})

    doc.close()
    return results


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Extract PDF pages as high-resolution PNG images."
    )
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("--output", "-o", default="./images", help="Output directory")
    parser.add_argument("--pages", type=int, nargs="+", help="Page numbers to extract (1-indexed)")
    parser.add_argument("--mapping", help="JSON string mapping page numbers to filenames")
    parser.add_argument("--all", dest="extract_all", action="store_true", help="Extract all pages")
    parser.add_argument("--zoom", type=float, default=2.0, help="Zoom factor (default: 2.0)")
    parser.add_argument("--prefix", default="", help="Filename prefix")
    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        print(f"Error: PDF not found: {args.pdf}")
        sys.exit(1)

    page_mapping = None
    if args.mapping:
        page_mapping = json.loads(args.mapping)

    results = extract_pages(
        pdf_path=args.pdf,
        output_dir=args.output,
        page_mapping=page_mapping,
        pages=args.pages,
        extract_all=args.extract_all,
        zoom=args.zoom,
        prefix=args.prefix,
    )

    success = sum(1 for r in results if r["status"] == "SUCCESS")
    skipped = sum(1 for r in results if r["status"] == "SKIPPED")
    print(f"\nDone: {success} extracted, {skipped} skipped.")

    if skipped > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
