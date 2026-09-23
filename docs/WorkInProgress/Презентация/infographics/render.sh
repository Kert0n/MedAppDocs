#!/bin/sh
# Сборка инфографики: тема ФКН + тело схемы → SVG и PNG.
set -e
cd "$(dirname "$0")"
MMDC=$(ls -d ~/.npm/_npx/*/node_modules/.bin/mmdc | head -1)
for body in *.body; do
  name=${body%.body}
  cat theme.txt "$body" > "$name.mmd"
  "$MMDC" -q -C font.css -i "$name.mmd" -o "$name.svg" -b white
  "$MMDC" -q -C font.css -i "$name.mmd" -o "$name.png" -b white -s 2
done
# Схема двух баз рисуется вручную: соответствие таблиц держится на раскладке.
python3 databases.py
PUPPETEER=$(dirname "$MMDC")/../puppeteer node svg2png.js 08-databases.svg 08-databases.png 2
