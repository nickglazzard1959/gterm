#!/bin/bash
echo "Build ctelnet minimal telnet client"
gcc ctelnet.c -o ctelnet
sudo cp ctelnet /usr/local/bin
#
# Fix some Apple insanity, at least until Apple further "improves
# security" ... which is likely to happen.
#
if [[ "$OSTYPE" == "darwin"* ]]; then
    sudo codesign --force --deep --sign - /usr/local/bin/ctelnet
fi
echo "Done."
