#!/usr/bin/env python
"""
Build urop-report.docx from urop-report.md.

- Downscales/embeds figures at a sensible resolution (photos -> JPEG, diagrams -> PNG).
- Expands <!-- PB --> markers into real Word page breaks.
- Inserts an auto-updating Contents field (Word: right-click -> Update Field, or F9).

Requires: pypandoc-binary, Pillow  (pip install pypandoc-binary Pillow)
Run from the report/ directory:  python build-docx.py
"""
import os, re, shutil
import pypandoc
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

SRC = "urop-report.md"
OUT = "urop-report.docx"
BUILD_ASSETS = ".build-assets"
MAXDIM = 1500

# PNGs that are line-art / screenshots with text -> keep as PNG to stay legible.
DIAGRAM_PNGS = {
    "pinout-connections.png", "db25-cover-shorts.png", "testpads-connection.png",
    "offset-enc-pcb-components.png", "testpad-map.png", "battery-v2-cad.png",
    "cell-voltage.png",
}

def main():
    text = open(SRC, encoding="utf-8").read()

    if os.path.isdir(BUILD_ASSETS):
        shutil.rmtree(BUILD_ASSETS)
    os.makedirs(BUILD_ASSETS)

    # --- downscale every referenced image, remap its path ---
    paths = list(dict.fromkeys(re.findall(r'!\[[^\]]*\]\(([^)]+)\)', text)))
    for p in paths:
        absp = os.path.normpath(os.path.join(HERE, p))
        if not os.path.isfile(absp):
            print("  MISSING:", p)
            continue
        base = os.path.basename(p)
        ext = os.path.splitext(base)[1].lower()
        im = Image.open(absp)
        w, h = im.size
        scale = min(1.0, MAXDIM / max(w, h))
        if scale < 1.0:
            im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        as_png = ext == ".png" and base in DIAGRAM_PNGS
        if as_png:
            outname = re.sub(r'[^A-Za-z0-9._-]', '_', p.replace("../", ""))
            im.save(os.path.join(BUILD_ASSETS, outname), optimize=True)
        else:  # photos (jpg/jpeg or photographic png) -> JPEG
            outname = re.sub(r'[^A-Za-z0-9._-]', '_', p.replace("../", ""))
            outname = os.path.splitext(outname)[0] + ".jpg"
            im.convert("RGB").save(os.path.join(BUILD_ASSETS, outname),
                                   "JPEG", quality=82, optimize=True)
        text = text.replace("(" + p + ")", "(" + BUILD_ASSETS + "/" + outname + ")")

    # --- page breaks ---
    pb = "\n```{=openxml}\n<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>\n```\n"
    text, npb = re.subn(r'(?m)^<!-- PB -->\s*$', lambda m: pb, text)
    print("  page breaks:", npb)

    build_md = "urop-report.build.md"
    open(build_md, "w", encoding="utf-8").write(text)
    try:
        pypandoc.convert_file(
            build_md, "docx", outputfile=OUT,
            extra_args=["--toc", "--toc-depth=2", "--resource-path=.",
                        "-f", "markdown-implicit_figures"],
        )
    finally:
        os.remove(build_md)
        shutil.rmtree(BUILD_ASSETS)

    print("  built %s (%.2f MB)" % (OUT, os.path.getsize(OUT) / 1e6))

if __name__ == "__main__":
    main()
