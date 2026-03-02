#!/usr/bin/env python3
"""Generic browser screenshot capture tool for tech blog writing.

Takes a JSON config (or CLI args) specifying URLs and scroll positions,
captures screenshots using Playwright, and saves them to an output directory.
Supports viewport scrolls, full-page capture, and optional selector-based
region capture (hero, architecture diagram, benchmark table, etc.).

When running inside Cursor or Claude Code, the agent may use MCP browser
tools (e.g. browser_navigate, browser_take_screenshot) instead of this script
for interactive or JS-heavy pages; this script is for batch headless capture.

Author: Damon Li

Usage:
    # Mode 1: CLI args for quick single-page capture
    python capture_screenshots.py --url https://example.com --output ./images

    # Mode 2: JSON config for batch multi-page capture
    python capture_screenshots.py --config screenshots.json

    # Mode 3: Inline JSON tasks
    python capture_screenshots.py --output ./images --tasks '[
        {"url": "https://example.com", "name": "homepage", "scrolls": [0, 1, 2]}
    ]'

JSON config format (screenshots.json):
    {
        "output_dir": "./images",
        "viewport": {"width": 1920, "height": 1080},
        "tasks": [
            {
                "url": "https://www.example.com/",
                "name": "example_homepage",
                "wait_seconds": 5,
                "scrolls": [0, 1, 2],
                "scroll_names": ["hero", "features", "footer"]
            },
            {
                "url": "https://docs.example.com/",
                "name": "example_docs",
                "wait_seconds": 3,
                "full_page": true
            },
            {
                "url": "https://product.example.com/",
                "name": "product_hero",
                "selectors": ["[data-hero]", ".architecture-diagram", "main .benchmark"],
                "selector_names": ["hero", "architecture", "benchmark"]
            }
        ]
    }

Dependencies:
    pip install playwright
    playwright install chromium
"""

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass, field

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: playwright is not installed.")
    print("Run: pip install playwright && playwright install chromium")
    sys.exit(1)


@dataclass
class ScreenshotTask:
    """Configuration for a single screenshot task."""

    url: str
    name: str
    wait_seconds: float = 3.0
    scrolls: list[float] = field(default_factory=lambda: [0])
    scroll_names: list[str] = field(default_factory=list)
    full_page: bool = False
    timeout_ms: int = 20000
    selectors: list[str] = field(default_factory=list)
    selector_names: list[str] = field(default_factory=list)


@dataclass
class CaptureConfig:
    """Top-level configuration for the capture session."""

    output_dir: str = "./images"
    viewport_width: int = 1920
    viewport_height: int = 1080
    tasks: list[ScreenshotTask] = field(default_factory=list)


def parse_config(args: argparse.Namespace) -> CaptureConfig:
    """Build CaptureConfig from CLI arguments or JSON file."""
    config = CaptureConfig()

    # JSON config file takes precedence
    if args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            data = json.load(f)
        config.output_dir = data.get("output_dir", config.output_dir)
        vp = data.get("viewport", {})
        config.viewport_width = vp.get("width", config.viewport_width)
        config.viewport_height = vp.get("height", config.viewport_height)
        for t in data.get("tasks", []):
            config.tasks.append(ScreenshotTask(
                url=t["url"],
                name=t["name"],
                wait_seconds=t.get("wait_seconds", 3.0),
                scrolls=t.get("scrolls", [0]),
                scroll_names=t.get("scroll_names", []),
                full_page=t.get("full_page", False),
                timeout_ms=t.get("timeout_ms", 20000),
                selectors=t.get("selectors", []),
                selector_names=t.get("selector_names", []),
            ))
        return config

    # Override output_dir from CLI
    if args.output:
        config.output_dir = args.output

    # Inline JSON tasks
    if args.tasks:
        task_list = json.loads(args.tasks)
        for t in task_list:
            config.tasks.append(ScreenshotTask(
                url=t["url"],
                name=t["name"],
                wait_seconds=t.get("wait_seconds", 3.0),
                scrolls=t.get("scrolls", [0]),
                scroll_names=t.get("scroll_names", []),
                full_page=t.get("full_page", False),
                selectors=t.get("selectors", []),
                selector_names=t.get("selector_names", []),
            ))
        return config

    # Single URL mode
    if args.url:
        name = args.name or args.url.split("//")[-1].split("/")[0].replace(".", "_")
        config.tasks.append(ScreenshotTask(
            url=args.url,
            name=name,
            wait_seconds=args.wait or 3.0,
            scrolls=[0, 1, 2] if not args.full_page else [0],
            full_page=args.full_page,
        ))
        return config

    print("Error: provide --url, --config, or --tasks.")
    sys.exit(1)


async def run_capture(config: CaptureConfig) -> list[dict]:
    """Execute all screenshot tasks and return results."""
    os.makedirs(config.output_dir, exist_ok=True)
    results: list[dict] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": config.viewport_width, "height": config.viewport_height}
        )
        page = await context.new_page()

        for task in config.tasks:
            print(f"\n{'=' * 60}")
            print(f"Task: {task.name} -> {task.url}")
            print(f"{'=' * 60}")

            try:
                print(f"  Navigating to {task.url} ...")
                await page.goto(task.url, wait_until="domcontentloaded", timeout=task.timeout_ms)
                print(f"  Waiting {task.wait_seconds}s for page load ...")
                await asyncio.sleep(task.wait_seconds)

                title = await page.title()
                print(f"  Page title: {title}")

                if task.selectors:
                    for idx, selector in enumerate(task.selectors):
                        suffix = (
                            task.selector_names[idx]
                            if idx < len(task.selector_names)
                            else f"region_{idx}"
                        )
                        path = os.path.join(config.output_dir, f"{task.name}_{suffix}.png")
                        try:
                            locator = page.locator(selector).first
                            await locator.wait_for(state="visible", timeout=5000)
                            await locator.screenshot(path=path)
                            size = os.path.getsize(path)
                            print(f"  Saved (selector): {path} ({size / 1024:.1f} KB)")
                            results.append({"task": f"{task.name}/{suffix}", "path": path, "status": "SUCCESS", "size": size})
                        except Exception as sel_exc:
                            print(f"  Selector '{selector}' failed: {sel_exc}")
                            results.append({"task": f"{task.name}/{suffix}", "path": "N/A", "status": "FAILED", "error": str(sel_exc)})
                elif task.full_page:
                    # Full-page screenshot
                    path = os.path.join(config.output_dir, f"{task.name}_full.png")
                    await page.screenshot(path=path, full_page=True)
                    size = os.path.getsize(path)
                    print(f"  Saved: {path} ({size / 1024:.1f} KB)")
                    results.append({"task": task.name, "path": path, "status": "SUCCESS", "size": size})
                else:
                    # Scroll-based viewport screenshots
                    for i, scroll_pos in enumerate(task.scrolls):
                        suffix = (
                            task.scroll_names[i]
                            if i < len(task.scroll_names)
                            else f"section_{i}"
                        )
                        path = os.path.join(config.output_dir, f"{task.name}_{suffix}.png")

                        await page.evaluate(
                            f"window.scrollTo(0, window.innerHeight * {scroll_pos})"
                        )
                        await asyncio.sleep(1)
                        await page.screenshot(path=path, full_page=False)

                        size = os.path.getsize(path)
                        print(f"  Saved: {path} ({size / 1024:.1f} KB)")
                        results.append({"task": f"{task.name}/{suffix}", "path": path, "status": "SUCCESS", "size": size})

            except Exception as exc:
                print(f"  ERROR: {exc}")
                results.append({"task": task.name, "path": "N/A", "status": "FAILED", "error": str(exc)})

        await browser.close()

    return results


def print_summary(results: list[dict]) -> None:
    """Print a final summary of all captured screenshots."""
    print(f"\n{'=' * 60}")
    print("CAPTURE SUMMARY")
    print(f"{'=' * 60}")

    success = [r for r in results if r["status"] == "SUCCESS"]
    failed = [r for r in results if r["status"] == "FAILED"]

    for r in success:
        print(f"  OK   {r['path']} ({r['size'] / 1024:.1f} KB)")
    for r in failed:
        print(f"  FAIL {r['task']}: {r.get('error', 'unknown')}")

    print(f"\nTotal: {len(success)} success, {len(failed)} failed")


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Capture browser screenshots for tech blog images."
    )
    parser.add_argument("--url", help="Single URL to capture")
    parser.add_argument("--name", help="Base filename for the screenshots")
    parser.add_argument("--output", "-o", help="Output directory (default: ./images)")
    parser.add_argument("--config", "-c", help="Path to JSON config file")
    parser.add_argument("--tasks", help="Inline JSON array of tasks")
    parser.add_argument("--wait", type=float, default=3.0, help="Seconds to wait after page load")
    parser.add_argument("--full-page", action="store_true", help="Capture full page instead of viewport sections")
    args = parser.parse_args()

    config = parse_config(args)
    results = asyncio.run(run_capture(config))
    print_summary(results)

    if any(r["status"] == "FAILED" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
