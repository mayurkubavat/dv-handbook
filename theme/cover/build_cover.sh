#!/usr/bin/env bash
# Build the cover: regenerate SVGs, render a 2-page 7x10in PDF with embedded fonts, plus PNG previews.
# Requires: brew install librsvg poppler; brew install --cask font-source-sans-3 font-source-serif-4 font-jetbrains-mono
set -euo pipefail
cd "$(dirname "$0")"
command -v rsvg-convert >/dev/null || { echo "rsvg-convert missing: brew install librsvg" >&2; exit 1; }
for f in "Source Sans 3" "Source Serif 4" "JetBrains Mono"; do
  if ! fc-list : family | grep -i "$f" >/dev/null; then echo "warning: font '$f' not installed; fallback will be used" >&2; fi
done
python3 gen_cover.py
rsvg-convert -f pdf -o cover.pdf front.svg back.svg          # page 1 front, page 2 back, 7x10in each
rsvg-convert -f png -w 700 -o front-preview.png front.svg
rsvg-convert -f png -w 700 -o back-preview.png back.svg
pdfinfo cover.pdf | grep -E 'Pages|Page size'
pdffonts cover.pdf | tail -n +3 | awk '{print $1, $NF}' | sort -u
