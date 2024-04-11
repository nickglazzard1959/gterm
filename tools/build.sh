#!/bin/bash
echo "Build font texture image, position and unicode map, and virtual keyboard image."
echo "==="
echo "Inputs are aplvkb.jsn, mainfont.png"
echo "Outputs are aplvkb.png, mainfonttexture.png, mainfonttexture.jsn, mainfontunicode.jsn"
echo "==="
rm -f aplvkb.png
rm -f mainfonttexture.png
rm -f mainfonttexture.jsn
rm -f mainfontunicode.jsn
python getmetrics.py -c 8x16
python makevkb.py -i ../gterm/aplvkb.jsn -o aplvkb.png
python mainfontunicode.py
rm -f celltest_*.png
rm -f ZZ*.png
echo "==="

