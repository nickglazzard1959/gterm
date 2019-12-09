#!/bin/bash
echo "Build ctelnet minimal telnet client"
gcc ctelnet.c -o ctelnet
sudo cp ctelnet /usr/local/bin
echo "Done."
