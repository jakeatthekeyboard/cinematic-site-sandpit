#!/usr/bin/env python3
"""Generate cinematic images for Ritch's Engraving v2.
Based on actual products from ritchsengraving.co.za:
- No hands, no people, no workshop shots
- Finished engraved products only, product photography style
- Silver name plates, engraved rings, tankards, trophies, plaques
"""

import os
import sys
import time
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


client = genai.Client(api_key=_api_key())
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")

images = [
    ("hero.png", (
        "Cinematic close-up product photography of an ornate sterling silver jewellery box "
        "with a polished engraved name plate on top, surrounded by intricate rose and scroll "
        "filigree borders. Deep red velvet lining visible. Shot on black background with "
        "dramatic side lighting creating reflections on the polished silver. No hands, no people. "
        "Shallow depth of field, dark moody atmosphere. 8K quality, luxury product advertisement."
    )),
    ("gallery-1-silver-box.png", (
        "Professional product photography of an engraved sterling silver cigarette case or card holder "
        "with elaborate hand-engraved scrollwork covering the entire surface. Sitting on dark velvet. "
        "Dramatic rim lighting highlighting the depth of the engraving cuts. No hands, no people. "
        "Dark background, cinematic lighting. 8K quality, luxury product shot."
    )),
    ("gallery-2-knife.png", (
        "Professional product photography of a custom engraved folding knife with detailed scrollwork "
        "on the bolsters and a Damascus steel blade, displayed open on aged dark leather. "
        "Cinematic side lighting creating dramatic shadows. No hands, no people. "
        "Dark moody background, shallow depth of field. 8K quality."
    )),
    ("gallery-3-trophy.png", (
        "Professional product photography of a silver-plated trophy tankard with laser-engraved text "
        "and a company logo on its surface, sitting on a dark wooden surface. Polished silver reflects "
        "warm studio light. No hands, no people. Dark background with a single accent light. "
        "8K quality, corporate awards photography style."
    )),
    ("gallery-4-crest.png", (
        "Professional product photography of a hand-engraved brass plate showing an elaborate heraldic "
        "family crest with a shield, lion supporters, a banner with Latin motto, and ornate mantling. "
        "Mounted on dark wood. Dramatic directional lighting from the left. No hands, no people. "
        "Dark moody atmosphere. 8K quality."
    )),
    ("gallery-5-ring.png", (
        "Professional product photography of a pair of engraved platinum wedding bands with intricate "
        "hand-engraved Celtic knot patterns, displayed on a dark velvet ring cushion. "
        "Cinematic lighting with soft golden reflections on the polished metal. No hands, no people. "
        "Shallow depth of field, dark background. 8K quality, luxury jewellery advertisement."
    )),
    ("gallery-6-zippo.png", (
        "Professional product photography of an engraved Zippo lighter with a detailed skull and roses "
        "design covering the entire case, lid closed, standing upright on a dark slate surface. "
        "Dramatic side lighting creating long shadows and highlighting the engraving depth. "
        "No hands, no people. Dark cinematic background. 8K quality."
    )),
    ("heritage.png", (
        "Cinematic still life of traditional hand engraving tools arranged on a dark aged wooden surface: "
        "several steel burins and gravers with wooden handles, a small brass vise, a magnifying loupe, "
        "and curls of metal shavings. Warm tungsten accent light from the side, dust particles in the air. "
        "No hands, no people. Dark atmospheric background. 8K quality, fine art still life photography."
    )),
]

for filename, prompt in images:
    path = os.path.join(IMAGE_DIR, filename)
    backup = path + ".v1"
    if os.path.exists(path) and not os.path.exists(backup):
        os.rename(path, backup)

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
            if os.path.exists(backup):
                os.rename(backup, path)
    except Exception as e:
        print(f"  FAIL {filename} — {e}")
        if os.path.exists(backup):
            os.rename(backup, path)

    print("  Waiting 25s...")
    time.sleep(25)

print("Done. v1 backups saved as *.v1")
