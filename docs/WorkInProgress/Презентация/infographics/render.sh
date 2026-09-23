#!/bin/sh
# Сборка инфографики: mermaid-схемы (тема ФКН + тело) и ручные SVG → SVG и PNG.
set -e
cd "$(dirname "$0")"
MMDC=$(ls -d ~/.npm/_npx/*/node_modules/.bin/mmdc | head -1)
export PUPPETEER="$(dirname "$MMDC")/../puppeteer"
for body in *.body; do
  name=${body%.body}
  cat theme.txt "$body" > "$name.mmd"
  "$MMDC" -q -C font.css -i "$name.mmd" -o "$name.svg" -b white
  "$MMDC" -q -C font.css -i "$name.mmd" -o "$name.png" -b white -s 2
done
# Ручные схемы: смысл держится на раскладке, поэтому она задана явно.
for script in databases.py capabilities.py claim.py knowledge.py; do
  python3 "$script"
done
for svg in 08-databases.svg 00-capabilities.svg 09-claim.svg 10-knowledge.svg; do
  node svg2png.js "$svg" "${svg%.svg}.png" 2
done
