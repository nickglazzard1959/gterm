#!/bin/bash
python getmetrics.py -c 8x16
python makevkb.py -i aplvkb.jsn -o aplvkb.png
python mainfontunicode.py
