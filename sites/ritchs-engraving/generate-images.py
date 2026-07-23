#!/usr/bin/env python3
"""Generate cinematic images for Ritch's Engraving site using Gemini (Nano Banana 2)."""

import os
import sys
import time
import base64
from pathlib import Path
from google import genai
from google.genai import types

def _api_key():
    """Gemini API key, environment only.

    This file used to carry a hardcoded key as a literal default. It leaked to a
    PUBLIC repo, Google's automated scanner caught it, and the key now returns
    403 PERMISSION_DENIED "Your API key was reported as leaked." Never inline a
    credential again -- fail loud instead, so a missing key is a clear error
    rather than a silent fallback to a committed secret.
    """
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY is not set. export GEMINI_API_KEY=... and re-run.")
    return key


API_KEY = _api_key()
OUTPUT_DIR = Path(__file__).parent / "images"
OUTPUT_DIR.mkdir(exist_ok=True)

client = genai.Client(api_key=API_KEY)

PROMPTS = {
    "hero": (
        "Dramatic close-up photograph of a master engraver's hands working on a silver ring "
        "with a burin tool, warm workshop lighting, shallow depth of field, golden hour light "
        "streaming through a window, metal shavings catching the light, dark moody atmosphere, "
        "cinematic color grading with warm gold and deep shadow tones, 16:9 aspect ratio, "
        "professional product photography quality"
    ),
    "gallery-1-silver-box": (
        "Ornate hand-engraved sterling silver jewelry box with intricate scrollwork patterns, "
        "dramatic side lighting on black velvet, museum-quality product photography, "
        "sharp detail on the engraved filigree, dark background, cinematic warm gold highlights"
    ),
    "gallery-2-knife": (
        "Custom engraved Damascus steel hunting knife with detailed scrollwork on the bolster, "
        "dramatic lighting against dark leather background, close-up showing the engraving detail, "
        "cinematic color grading, professional product photography, moody atmosphere"
    ),
    "gallery-3-trophy": (
        "Crystal trophy award with laser-engraved corporate logo, dramatic backlit photography, "
        "light refracting through crystal creating rainbow prisms, dark studio background, "
        "elegant and premium feel, sharp focus on the engraved text"
    ),
    "gallery-4-crest": (
        "Detailed heraldic family crest engraved into a polished brass plate, dramatic raking "
        "light showing the depth of the engraving, dark background, museum lighting, "
        "ultra-detailed macro photography showing tool marks and craftsmanship"
    ),
    "gallery-5-ring": (
        "Close-up macro photograph of a gold wedding band with hand-engraved Celtic knot pattern, "
        "sitting on dark slate, soft bokeh background with warm golden light, "
        "shallow depth of field, romantic cinematic mood, professional jewelry photography"
    ),
    "gallery-6-zippo": (
        "Collection of three engraved Zippo lighters with different designs — skull, eagle, and "
        "vintage car — arranged on dark wood surface, dramatic top-down lighting, "
        "polished brass catching warm light, cinematic product photography"
    ),
    "heritage": (
        "Atmospheric photograph of an artisan engraving workshop, wooden workbench covered in tools "
        "— burins, gravers, magnifying glass, brass shavings — warm afternoon light through dusty "
        "windows, Bo-Kaap Cape Town character, lived-in authentic workshop feel, cinematic "
        "documentary style photography, depth and atmosphere, 3:4 portrait aspect ratio"
    ),
}

def generate_image(name, prompt):
    out_path = OUTPUT_DIR / f"{name}.png"
    if out_path.exists():
        print(f"  [skip] {name} already exists")
        return

    print(f"  [gen] {name}...")
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_data = part.inline_data.data
                with open(out_path, "wb") as f:
                    f.write(image_data)
                print(f"  [ok] {name} → {out_path} ({len(image_data)} bytes)")
                return

        print(f"  [warn] {name}: no image in response")
    except Exception as e:
        print(f"  [err] {name}: {e}")

if __name__ == "__main__":
    print(f"Generating {len(PROMPTS)} images into {OUTPUT_DIR}/\n")
    remaining = [(n, p) for n, p in PROMPTS.items() if not (OUTPUT_DIR / f"{n}.png").exists()]
    print(f"  {len(PROMPTS) - len(remaining)} already exist, {len(remaining)} to generate\n")
    for i, (name, prompt) in enumerate(remaining):
        if i > 0:
            print(f"  [wait] 15s cooldown...")
            time.sleep(15)
        generate_image(name, prompt)
    print("\nDone.")
