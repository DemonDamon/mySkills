#!/usr/bin/env python3
"""Download PDF files from URLs to a local directory for tech blog sources.

Used in Phase 1 to ensure all paper/report PDF links are saved under
sources/pdfs/ for later extraction and reference. Uses only stdlib + requests.

Author: Damon Li

Usage:
    python download_pdfs.py -o <output_dir>/sources/pdfs --url "https://arxiv.org/pdf/2301.xxx.pdf"
    python download_pdfs.py -o ./sources/pdfs --urls-file urls.txt
    python download_pdfs.py -o ./sources/pdfs --url "https://..." "https://..."

Dependencies:
    pip install requests
"""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Error: requests is not installed. Run: pip install requests")
    sys.exit(1)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
TIMEOUT = 60
MAX_FILENAME_LEN = 120


def _safe_filename(url: str, index: int) -> str:
    """Build a safe PDF filename from URL or index."""
    path = urlparse(url).path or ""
    base = Path(path).stem or f"pdf_{index}"
    base = re.sub(r"[^\w\-.]", "_", base)[:MAX_FILENAME_LEN]
    if not base:
        base = f"pdf_{index}"
    return f"{base}.pdf"


def download_one(url: str, output_dir: Path, filename: str | None = None) -> dict:
    """Download a single PDF from URL to output_dir. Returns result dict."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
            allow_redirects=True,
            stream=True,
        )
        resp.raise_for_status()
        content_type = (resp.headers.get("Content-Type") or "").lower()
        if "pdf" not in content_type and not url.lower().endswith(".pdf"):
            return {
                "url": url,
                "status": "SKIP",
                "path": None,
                "error": f"Content-Type is not PDF: {content_type}",
            }

        name = filename or _safe_filename(url, 0)
        out_path = output_dir / name
        with open(out_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
        size = out_path.stat().st_size
        return {"url": url, "status": "SUCCESS", "path": str(out_path), "size": size}
    except requests.RequestException as e:
        return {"url": url, "status": "FAILED", "path": None, "error": str(e)}
    except OSError as e:
        return {"url": url, "status": "FAILED", "path": None, "error": str(e)}


def run_download(urls: list[str], output_dir: str | Path, urls_file: str | None = None) -> list[dict]:
    """Download all PDFs; URLs can come from list or from file (one URL per line)."""
    if urls_file:
        path = Path(urls_file)
        if path.is_file():
            urls = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    urls = [u for u in urls if u and (u.startswith("http://") or u.startswith("https://"))]
    if not urls:
        return []

    output_dir = Path(output_dir)
    results = []
    for i, url in enumerate(urls):
        filename = _safe_filename(url, i + 1)
        result = download_one(url, output_dir, filename=filename)
        results.append(result)
        if result["status"] == "SUCCESS":
            print(f"  OK   {result['path']} ({result['size'] / 1024:.1f} KB)")
        else:
            print(f"  FAIL {url}: {result.get('error', result['status'])}")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download PDF files from URLs to a local directory (e.g. sources/pdfs).",
    )
    parser.add_argument("-o", "--output-dir", required=True, help="Output directory (e.g. <output_dir>/sources/pdfs)")
    parser.add_argument("--url", action="append", default=[], help="PDF URL (can be repeated)")
    parser.add_argument("--urls-file", help="Text file with one PDF URL per line")
    args = parser.parse_args()

    urls = args.url or []
    results = run_download(urls, args.output_dir, urls_file=args.urls_file)

    if not results:
        print("No URLs to download. Use --url or --urls-file.")
        sys.exit(1)

    success = sum(1 for r in results if r["status"] == "SUCCESS")
    print(f"\nDone: {success}/{len(results)} downloaded to {args.output_dir}")
    if success < len(results):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
