#!/usr/bin/env python3
"""Generate the 3 remaining cinematic images for Ritch's Engraving."""

import os
import sys
import time
from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyD_goDtJUANpLN2XwcKpinEMg3aoNhYypQ")
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")

remaining = [
    ("gallery-5-ring.png", (
        "Professional product photography of a hand-engraved platinum wedding ring "
        "on a dark velvet cushion. Cinematic lighting with dramatic rim light highlighting "
        "the intricate scrollwork pattern. Shallow depth of field, dark moody background "
        "with warm golden accent light. 8K quality, luxury jewelry advertisement style."
    )),
    ("gallery-6-zippo.png", (
        "Professional product photography of a custom-engraved Zippo lighter with detailed "
        "artwork on its surface, sitting on aged dark wood. Cinematic lighting with the lid "
        "open showing the flame mechanism. Dramatic side lighting creating long shadows. "
        "Dark moody atmosphere, copper and gold tones. 8K quality, luxury product shot."
    )),
    ("heritage.png", (
        "Cinematic wide shot of a master engraver's workshop. Warm tungsten lighting "
        "illuminating an aged wooden workbench covered with traditional hand engraving tools — "
        "burins, gravers, magnifying loupes, brass plates. Dust particles visible in light beams. "
        "Dark atmospheric background with shelves of completed works. Film grain texture, "
        "moody documentary photography style. 8K quality."
    )),
]

for filename, prompt in remaining:
    path = os.path.join(IMAGE_DIR, filename)
    if os.path.exists(path):
        print(f"SKIP {filename} (exists)")
        continue

    print(f"Generating {filename}...")
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"]),
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                with open(path, "wb") as f:
                    f.write(part.inline_data.data)
                size_kb = os.path.getsize(path) / 1024
                print(f"  OK  {filename} ({size_kb:.0f} KB)")
                break
        else:
            print(f"  FAIL {filename} — no image in response")
    except Exception as e:
        print(f"  FAIL {filename} — {e}")

    print("  Waiting 25s before next request...")
    time.sleep(25)

print("Done.")
