#!/usr/bin/env python3
"""Image quality filter for tech blog assets.

Scans an images directory, classifies each image as A/B/C grade, moves C-grade
(noise) images to _noise/, and writes image_audit.json with per-file rationale.
Uses Pillow for dimensions and entropy; no heavy ML dependencies.

Author: Damon Li

Usage:
    python image_filter.py --images-dir <output_dir>/images
    python image_filter.py -i ./images --min-size 120 --dry-run

Dependencies:
    pip install Pillow
"""

import argparse
import json
import math
import re
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is not installed. Run: pip install Pillow")
    sys.exit(1)

# Minimum dimension (px); smaller images are treated as favicon/icon and removed
DEFAULT_MIN_DIM = 100
# Minimum file size (bytes); smaller files are removed
DEFAULT_MIN_BYTES = 5 * 1024
# Filename patterns that suggest UI chrome (C-grade)
NOISE_FILENAME_PATTERN = re.compile(
    r"favicon|icon|logo|avatar|badge|shield|spinner|loading",
    re.IGNORECASE,
)
# Aspect ratio bounds; outside these are treated as banners/separators (C-grade)
MAX_ASPECT_RATIO = 10.0
MIN_ASPECT_RATIO = 1 / 10.0
# Entropy threshold; below this suggests near-solid color (C-grade)
MIN_ENTROPY = 2.0

AUDIT_FILENAME = "image_audit.json"
NOISE_SUBDIR = "_noise"

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def _image_entropy(img: Image.Image) -> float:
    """Compute grayscale histogram entropy as a proxy for content richness."""
    gray = img.convert("L")
    hist = gray.histogram()
    total = sum(hist)
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in hist:
        if count > 0:
            p = count / total
            entropy -= p * math.log(p)
    return entropy


def _classify_one(
    path: Path,
    min_dim: int,
    min_bytes: int,
) -> tuple[str, list[str]]:
    """Classify a single image as A, B, or C and return (grade, reasons)."""
    reasons: list[str] = []
    stat = path.stat()
    name_lower = path.name.lower()

    # File size
    if stat.st_size < min_bytes:
        return "C", [f"file size {stat.st_size} < {min_bytes} bytes"]

    # Filename pattern (C-grade if matches noise pattern)
    if NOISE_FILENAME_PATTERN.search(path.name):
        reasons.append("filename matches noise pattern (favicon/icon/logo/...)")

    try:
        with Image.open(path) as img:
            w, h = img.size
            # Dimension filter: too small -> C and effectively removed
            if w < min_dim or h < min_dim:
                return "C", [f"dimension {w}x{h} below min {min_dim}px"]

            # Aspect ratio
            ratio = max(w, h) / max(min(w, h), 1)
            if ratio > MAX_ASPECT_RATIO or ratio < MIN_ASPECT_RATIO:
                reasons.append(f"extreme aspect ratio {ratio:.2f}")

            # Entropy (only for non-tiny images)
            if w * h >= min_dim * min_dim:
                entropy = _image_entropy(img)
                if entropy < MIN_ENTROPY:
                    reasons.append(f"low entropy {entropy:.2f} (near-solid color)")
    except Exception as e:
        return "C", [f"unreadable or invalid image: {e}"]

    if reasons:
        return "C", reasons
    # A: screenshot / architecture / benchmark; B: other contentful images
    if "screenshot" in name_lower or "architecture" in name_lower or "benchmark" in name_lower:
        return "A", []
    return "B", []


def run_filter(
    images_dir: str | Path,
    min_dim: int = DEFAULT_MIN_DIM,
    min_bytes: int = DEFAULT_MIN_BYTES,
    dry_run: bool = False,
) -> dict:
    """Scan images_dir, classify files, move C-grade to _noise/, write audit JSON."""
    images_dir = Path(images_dir)
    if not images_dir.is_dir():
        return {"error": f"not a directory: {images_dir}", "audit": [], "moved": []}

    noise_dir = images_dir / NOISE_SUBDIR
    if not dry_run:
        noise_dir.mkdir(parents=True, exist_ok=True)

    audit: list[dict] = []
    moved: list[str] = []

    for path in sorted(images_dir.iterdir()):
        if path.is_dir() and path.name == NOISE_SUBDIR:
            continue
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        grade, reasons = _classify_one(path, min_dim, min_bytes)
        rel_path = path.name
        audit.append({
            "file": rel_path,
            "grade": grade,
            "reasons": reasons,
        })

        if grade == "C":
            dest = noise_dir / path.name
            if not dry_run:
                shutil.move(str(path), str(dest))
            moved.append(rel_path)

    audit_path = images_dir / AUDIT_FILENAME
    if not dry_run and audit:
        with open(audit_path, "w", encoding="utf-8") as f:
            json.dump({"audit": audit, "moved": moved}, f, ensure_ascii=False, indent=2)

    summary = {
        "A": sum(1 for a in audit if a["grade"] == "A"),
        "B": sum(1 for a in audit if a["grade"] == "B"),
        "C": sum(1 for a in audit if a["grade"] == "C"),
        "moved": len(moved),
    }
    return {"summary": summary, "audit": audit, "moved": moved, "audit_path": str(audit_path)}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Filter low-quality images and write image_audit.json.",
    )
    parser.add_argument(
        "-i", "--images-dir",
        required=True,
        help="Path to images directory (e.g. <output_dir>/images)",
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=DEFAULT_MIN_DIM,
        help=f"Minimum width/height in pixels (default: {DEFAULT_MIN_DIM})",
    )
    parser.add_argument(
        "--min-bytes",
        type=int,
        default=DEFAULT_MIN_BYTES,
        help=f"Minimum file size in bytes (default: {DEFAULT_MIN_BYTES})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only classify and print; do not move files or write audit",
    )
    args = parser.parse_args()

    result = run_filter(
        args.images_dir,
        min_dim=args.min_size,
        min_bytes=args.min_bytes,
        dry_run=args.dry_run,
    )

    if "error" in result:
        print(result["error"])
        sys.exit(1)

    s = result["summary"]
    print(f"A (high value): {s['A']}, B (usable): {s['B']}, C (noise, moved): {s['C']}")
    if result["moved"]:
        print(f"Moved to {NOISE_SUBDIR}/: {', '.join(result['moved'][:10])}{'...' if len(result['moved']) > 10 else ''}")
    if not args.dry_run and result.get("audit_path"):
        print(f"Audit written to: {result['audit_path']}")


if __name__ == "__main__":
    main()
