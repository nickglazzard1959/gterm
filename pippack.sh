#! /usr/bin/bash
rm -rf package/gterm/gterm
mkdir -p package/gterm/gterm
#
cp README.md package/gterm
#
cp gterm.py package/gterm/gterm
cp main.py package/gterm/gterm
cp __main__.py package/gterm/gterm
cp __init__.py package/gterm/gterm
#
cp gterm.png package/gterm/gterm
cp gtermicon.png package/gterm/gterm
cp aplvkb.jsn package/gterm/gterm
cp aplvkb.png package/gterm/gterm
cp mainfonttexture.jsn package/gterm/gterm
cp mainfonttexture.png package/gterm/gterm
cp mainfontunicode.jsn package/gterm/gterm
cp kling.wav package/gterm/gterm
cp beep-3.wav package/gterm/gterm
#
cd package/gterm
pip install .
#
rm -rf build gterm.egg-info
cd gterm
rm -f *~
cd ../..
rm -f gterm.zip
zip -r -v gterm.zip gterm
