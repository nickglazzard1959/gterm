#!/bin/bash
echo "Use APT package manager to install binary prerequisites"
sudo apt install portaudio19-dev
sudo apt install python-all-dev
sudo apt install pkg-config
sudo apt install libcairo2-dev
if [ "$XDG_SESSION_TYPE" == "x11" ]; then
    sudo apt install xclip
else
    sudo apt install wl-clipboard
fi
