#!/bin/bash
# NOTE: This requires a full TeX/LaTeX system is available.
# On Linux, that could be TeXLive. On MacOS, MacTeX. These
# are huge packages. Also, at least on Debian, some basic
# fonts seem to be missing by default. These must be obtained
# with:
# sudo apt-get install ttf-mscorefonts-installer
tar xzf epsfiles.tgz
xelatex gterm.tex
xelatex gterm.tex
xelatex gterm.tex
rm -f *.eps
