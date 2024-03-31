#! /usr/bin/bash
mkdir -p package/gterm/gterm
cp gterm.py package/gterm/gterm
cp gterm.png package/gterm/gterm
cp gtermicon.png package/gterm/gterm
cp aplvkb.jsn package/gterm/gterm
cp aplvkb.png package/gterm/gterm
cp mainfonttexture.jsn package/gterm/gterm
cp mainfonttexture.png package/gterm/gterm
cp mainfontunicode.jsn package/gterm/gterm
cp kling.wav package/gterm/gterm
cp beep-3.wav package/gterm/gterm
cd package/gterm
#pip install --verbose .
rm -rf build gterm.egg-info
rm -f *~
zip -r -v gterm.zip gterm
