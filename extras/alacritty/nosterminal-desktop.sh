#!/bin/bash
function show_help () {
    cat <<EOF

Usage: nosterminal-desktop.sh [-h] [host-ip-or-name [port-number]]

 Setup up Alacritty to emulate an NCD16 or 19 X terminal with typeahead
 for DtCyber using a standard full size keyboard. The key assignments are 
 the obvious mappings and are due to to Gerard van der Grinten.
 Unused options have been deleted to make the file short.

 For use with FSE (etc.):
 /TRMDEF,TC=7.
 /SCREEN,NCDXT.
                                                                
                 NCDX NOS Terminal Definition Key Mappings      
                                                                
                 Key       Modifier        Action               
             +------------------------------------------------+ 
             | F1 - F12  |          | F1 - F12                | 
             |           | Shift    | F1 - F12 Shifted        | 
             |------------------------------------------------| 
             | F1 - F4   | Ctrl     | F13 - F16               | 
             |           | Alt      | F13 - F16 Shifted       | 
             |------------------------------------------------| 
             | Insert    |          | Enter Insert Mode       | 
             |           | Shift    | Insert Line             | 
             |           | Ctrl     | Insert Character        | 
             |------------------------------------------------| 
             | Delete    |          | Delete Character        | 
             |           | Shift    | Delete Line             | 
             |------------------------------------------------| 
             | Home      |          | Put Cursor on Home Line | 
             |------------------------------------------------| 
             | End       |          | Exit Insert Mode        | 
             |           | Ctrl     | Delete to End of Line   | 
             |------------------------------------------------| 
             | Page Up   |          | Previous Screen         | 
             |           | Shift    | Top                     | 
             |           | Ctrl     | Half Page Forward       | 
             |------------------------------------------------| 
             | Page Down |          | Next Screen             | 
             |           | Shift    | Bottom                  | 
             |           | Ctrl     | Half Page Backward      | 
             +------------------------------------------------+ 
                                                                  
EOF
}

if [ "$#" -gt 2 ]; then
    show_help
    exit
fi

if [ "$#" -lt 1 ]; then
    host="127.0.0.1"
    port="23"
    echo "Trying localhost port 23. This may well fail."
    echo "Use -h for help."
else
    if [ "${1}" = "-h" ]; then
        show_help
        exit
    else
        host=${1}
        port="23"
        if [ "$#" -eq 2 ]; then
            port=${2}
        fi
    fi
fi

(
cat <<EOF
[bell]
animation = "EaseOutExpo"
color = "#ff1111"
duration = 50

[font]
size = 9.0

[colors.cursor]
cursor = "#b58900"
text = "CellBackground"

[colors.primary]
background = "#003863"
foreground = "#f0f0f0"

[cursor]
blink_interval = 250

[cursor.style]
blinking = "Off"
shape = "Block"

[[keyboard.bindings]]
chars = "\b"
key = "Back"

[[keyboard.bindings]]
chars = "\u001B[925~\r"
key = "F1"
mods = "Alt"

[[keyboard.bindings]]
chars = "\u001B[25~\r"
key = "F1"
mods = "Control"

[[keyboard.bindings]]
chars = "\u001B[911~\r"
key = "F1"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[11~\r"
key = "F1"

[[keyboard.bindings]]
chars = "\u001B[926~\r"
key = "F2"
mods = "Alt"

[[keyboard.bindings]]
chars = "\u001B[26~\r"
key = "F2"
mods = "Control"

[[keyboard.bindings]]
chars = "\u001B[912~\r"
key = "F2"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[12~\r"
key = "F2"

[[keyboard.bindings]]
chars = "\u001B[928~\r"
key = "F3"
mods = "Alt"

[[keyboard.bindings]]
chars = "\u001B[28~\r"
key = "F3"
mods = "Control"

[[keyboard.bindings]]
chars = "\u001B[913~\r"
key = "F3"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[13~\r"
key = "F3"

[[keyboard.bindings]]
chars = "\u001B[929~\r"
key = "F4"
mods = "Alt"

[[keyboard.bindings]]
chars = "\u001B[29~\r"
key = "F4"
mods = "Control"

[[keyboard.bindings]]
chars = "\u001B[914~\r"
key = "F4"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[14~\r"
key = "F4"

[[keyboard.bindings]]
chars = "\u001B[915~\r"
key = "F5"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[15~\r"
key = "F5"

[[keyboard.bindings]]
chars = "\u001B[917~\r"
key = "F6"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[17~\r"
key = "F6"

[[keyboard.bindings]]
chars = "\u001B[918~\r"
key = "F7"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[18~\r"
key = "F7"

[[keyboard.bindings]]
chars = "\u001B[919~\r"
key = "F8"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[19~\r"
key = "F8"

[[keyboard.bindings]]
chars = "\u001B[920~\r"
key = "F9"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[20~\r"
key = "F9"

[[keyboard.bindings]]
chars = "\u001B[921~\r"
key = "F10"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[21~\r"
key = "F10"

[[keyboard.bindings]]
chars = "\u001B[923~\r"
key = "F11"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[23~\r"
key = "F11"

[[keyboard.bindings]]
chars = "\u001B[924~\r"
key = "F12"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[24~\r"
key = "F12"

[[keyboard.bindings]]
chars = "\u001B[H"
key = "Home"

[[keyboard.bindings]]
chars = "\u001B\u001B[95~\r"
key = "PageUp"
mods = "Control"

[[keyboard.bindings]]
chars = "\u001B[95~\r"
key = "PageUp"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[5~\r"
key = "PageUp"

[[keyboard.bindings]]
chars = "\u001B[K"
key = "End"
mods = "Control"

[[keyboard.bindings]]
chars = "\u001B[4l"
key = "End"

[[keyboard.bindings]]
chars = "\u001B\u001B[96~\r"
key = "PageDown"
mods = "Control"

[[keyboard.bindings]]
chars = "\u001B[96~\r"
key = "PageDown"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[6~\r"
key = "PageDown"

[[keyboard.bindings]]
chars = "\u001B[@"
key = "Insert"
mods = "Control"

[[keyboard.bindings]]
chars = "\u001B[L"
key = "Insert"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[4h"
key = "Insert"

[[keyboard.bindings]]
chars = "\u001B[P"
key = "Delete"
mods = "Control"

[[keyboard.bindings]]
chars = "\u001B[M"
key = "Delete"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[P"
key = "Delete"

[window]
title = "Alacritty NCDXT Standard Keyboard"

[window.dimensions]
columns = 132
lines = 43

[keyboard]

EOF
) > /tmp/alacritty-ncdxt-desktop.toml
/usr/local/bin/alacritty --config-file /tmp/alacritty-ncdxt-desktop.toml -e /usr/local/bin/ctelnet ${host} ${port}
