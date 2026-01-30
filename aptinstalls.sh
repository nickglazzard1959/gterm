#!/bin/bash
echo "Use APT package manager to install binary prerequisites"
sudo apt update
sudo apt install build-essential
sudo apt install git
sudo apt install net-tools
sudo apt install python3-pip
sudo apt install python3-venv
sudo apt install python3-pyaudio
sudo apt install python3-dev
sudo apt install portaudio19-dev
sudo apt install pkg-config
sudo apt install libcairo2-dev
if [ "$XDG_SESSION_TYPE" == "x11" ]; then
    sudo apt install xclip
else
    sudo apt install wl-clipboard
fi
