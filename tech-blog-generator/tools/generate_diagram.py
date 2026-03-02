#!/usr/bin/env python3
"""Generate diagram images from NanoBanana-style visual prompts.

Supports Gemini API (google-genai) for closed-loop generation. When Gemini
is unavailable, writes the prompt to a file for manual use with Lovart.ai
or MCP text_to_image tools.

Author: Damon Li

Usage:
    python generate_diagram.py --prompt "视觉描述..." --output images/01_arch.jpg
    python generate_diagram.py --prompt-file visual-prompts/01_arch.txt -o images/01_arch.jpg --api gemini
    python generate_diagram.py --prompt "..." -o out.png --api fallback

Dependencies:
    pip install Pillow
    For Gemini: pip install google-genai
"""

import argparse
import os
import sys
from pathlib import Path

# Optional: Gemini
try:
    from google import genai
    from google.genai import types
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

GEMINI_MODEL = "gemini-2.0-flash-preview-image-generation"
# Fallback model name for image gen (may vary by region)
GEMINI_IMAGE_MODEL_ALT = "gemini-3-pro-image-preview"


def _load_prompt(prompt: str | None, prompt_file: str | None) -> str:
    if prompt_file:
        path = Path(prompt_file)
        if not path.is_file():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8").strip()
    if prompt:
        return prompt.strip()
    raise ValueError("Provide either --prompt or --prompt-file")


def generate_with_gemini(prompt: str, output_path: Path, aspect_ratio: str = "16:9") -> bool:
    """Generate image using Google Gemini API. Returns True on success."""
    if not HAS_GEMINI:
        return False
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return False

    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size="2K",
        ),
    )
    response = None
    for model_name in (GEMINI_IMAGE_MODEL_ALT, GEMINI_MODEL, "gemini-2.0-flash-preview-image-generation"):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[prompt],
                config=config,
            )
            break
        except Exception:
            continue
    if response is None:
        return False

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    parts = getattr(response, "candidates", None)
    if parts and len(parts) > 0:
        content = getattr(parts[0], "content", None)
        if content is not None:
            parts = getattr(content, "parts", parts)
    else:
        parts = getattr(response, "parts", [])

    for part in parts:
        inline = getattr(part, "inline_data", None)
        if inline is not None:
            data = getattr(inline, "data", None)
            if data is not None:
                mime = getattr(inline, "mime_type", None) or "image/png"
                ext = ".png" if "png" in (mime or "") else ".jpg"
                out = output_path.with_suffix(ext)
                out.write_bytes(data)
                return True
        if hasattr(part, "as_image") and callable(part.as_image):
            try:
                img = part.as_image()
                out = output_path.with_suffix(".png")
                img.save(str(out))
                return True
            except Exception:
                pass
    return False


def fallback_save_prompt(prompt: str, output_path: Path, prompts_dir: Path | None) -> str:
    """Save prompt to visual-prompts and return instructions for manual generation."""
    out = Path(output_path)
    prompts_dir = prompts_dir or (out.parent.parent / "visual-prompts")
    prompts_dir.mkdir(parents=True, exist_ok=True)
    stem = out.stem
    prompt_file = prompts_dir / f"{stem}.txt"
    prompt_file.write_text(prompt, encoding="utf-8")
    return (
        f"Prompt saved to {prompt_file}. "
        "Generate the image manually: use Lovart.ai (NanoBanana Pro) or the text_to_image MCP tool, "
        f"then save the result as {out.name} in {out.parent}."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate diagram image from a visual description prompt.",
    )
    parser.add_argument("--prompt", help="Visual description prompt (NanoBanana-style text)")
    parser.add_argument("--prompt-file", help="Path to a .txt file containing the prompt")
    parser.add_argument("-o", "--output", required=True, help="Output image path (e.g. images/01_arch.jpg)")
    parser.add_argument(
        "--api",
        choices=("gemini", "fallback"),
        default="gemini",
        help="Use gemini (default) or only save prompt (fallback)",
    )
    parser.add_argument(
        "--aspect",
        default="16:9",
        help="Aspect ratio for Gemini (default: 16:9)",
    )
    parser.add_argument(
        "--visual-prompts-dir",
        help="Directory for saving prompt when using fallback (default: <output_dir>/visual-prompts)",
    )
    args = parser.parse_args()

    prompt = _load_prompt(args.prompt, args.prompt_file)
    output_path = Path(args.output)

    if args.api == "fallback":
        prompts_dir = Path(args.visual_prompts_dir) if args.visual_prompts_dir else None
        msg = fallback_save_prompt(prompt, output_path, prompts_dir)
        print(msg)
        sys.exit(0)

    if args.api == "gemini" and HAS_GEMINI and os.environ.get("GEMINI_API_KEY"):
        if generate_with_gemini(prompt, output_path, args.aspect):
            print(f"Image saved: {output_path}")
            sys.exit(0)

    print("Gemini not available or generation failed. Using fallback.")
    prompts_dir = Path(args.visual_prompts_dir) if args.visual_prompts_dir else None
    msg = fallback_save_prompt(prompt, output_path, prompts_dir)
    print(msg)
    sys.exit(0)


if __name__ == "__main__":
    main()
