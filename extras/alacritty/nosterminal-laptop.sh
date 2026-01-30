#!/bin/bash
function show_help () {
    cat <<EOF

Usage: nosterminal-laptop.sh [-h] [host-ip-or-name [port-number]]

Run Alacritty with definitions that make it look like an NCD16/NCD19 
Xterminal with type ahead. This is primarily for use with the 
NOS 2.8.7 turnkey system which supports these terminals.

 The key assignments are my own and pretty
 idisyncratic (sure they could be improved on).
 Unused options have been deleted to make the file short.

 For use with FSE (etc.):
 /TRMDEF,TC=7.
 /SCREEN,NCDXT.

 Function keys (mostly as per FSE on screen guide):
         +----------+----------+----------+----------+----------+----------+----------+----------+
   KEY:  |    F1    |    F2    |    F3    |    F4    |    F5    |    F6    |    F7    |    F8    |
         +----------+----------+----------+----------+----------+----------+----------+----------+
   +CMD :| ........ | DEL LINE | ........ | ........ | ........ | ........ | ........ | ........ |
   +ALT :|   HOME   | DEL CHAR | ........ | ........ | ........ | ........ | ........ | ........ |
 +SHIFT :|  MRKCHR  |  ONECPY  | DEL BLK  |   LAST   |  UNMARK  | ........ |  LOCNXT  | 80 COL   |
  PLAIN :|   MARK   |   MOVE   | INS BLK  |   FIRST  |   UNDO   |   QUIT   |  LOCATE  | 132 COL  |
         +----------+----------+----------+----------+----------+----------+----------+----------+

 Arrow keys:
         +----------+----------+----------+----------+
   KEY:  |   LEFT   |    UP    |   DOWN   |   RIGHT  |
         +----------+----------+----------+----------+
   +CMD :| INS CHAR | PG/2 UP  |PG/2 DOWN | ........ |
   +ALT :| INS LINE |   TOP    |  BOTTOM  | DEL EOL  |
 +SHIFT :|  INSERT  | PAGE UP  | PG DOWN  | END INS  | 
  PLAIN :|   LEFT   |   UP     |   DOWN   |  RIGHT   |
         +----------+----------+----------+----------+             
                                                                             
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
duration = 150

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
chars = "\u001B[11~\r"
key = "F1"

[[keyboard.bindings]]
chars = "\u001B[911~\r"
key = "F1"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[J\r"
key = "F1"
mods = "Command"

[[keyboard.bindings]]
chars = "\u001B[H"
key = "F1"
mods = "Alt"

[[keyboard.bindings]]
chars = "\u001B[12~\r"
key = "F2"

[[keyboard.bindings]]
chars = "\u001B[912~\r"
key = "F2"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[M"
key = "F2"
mods = "Command"

[[keyboard.bindings]]
chars = "\u001B[P"
key = "F2"
mods = "Alt"

[[keyboard.bindings]]
chars = "\u001B[13~\r"
key = "F3"

[[keyboard.bindings]]
chars = "\u001B[913~\r"
key = "F3"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[28~\r"
key = "F3"
mods = "Command"

[[keyboard.bindings]]
chars = "\u001B[928~\r"
key = "F3"
mods = "Alt"

[[keyboard.bindings]]
chars = "\u001B[14~\r"
key = "F4"

[[keyboard.bindings]]
chars = "\u001B[914~\r"
key = "F4"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[29~\r"
key = "F4"
mods = "Command"

[[keyboard.bindings]]
chars = "\u001B[929~\r"
key = "F4"
mods = "Alt"

[[keyboard.bindings]]
chars = "\u001B[15~\r"
key = "F5"

[[keyboard.bindings]]
chars = "\u001B[915~\r"
key = "F5"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[17~\r"
key = "F6"

[[keyboard.bindings]]
chars = "\u001B[917~\r"
key = "F6"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[18~\r"
key = "F7"

[[keyboard.bindings]]
chars = "\u001B[918~\r"
key = "F7"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[19~\r"
key = "F8"

[[keyboard.bindings]]
chars = "\u001B[919~\r"
key = "F8"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[20~\r"
key = "F9"

[[keyboard.bindings]]
chars = "\u001B[920~\r"
key = "F9"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[21~\r"
key = "F10"

[[keyboard.bindings]]
chars = "\u001B[921~\r"
key = "F10"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[23~\r"
key = "F11"

[[keyboard.bindings]]
chars = "\u001B[923~\r"
key = "F11"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[24~\r"
key = "F12"

[[keyboard.bindings]]
chars = "\u001B[924~\r"
key = "F12"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[5~\r"
key = "Up"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[95~\r"
key = "Up"
mods = "Alt"

[[keyboard.bindings]]
chars = "\u001B\u001B[95~\r"
key = "Up"
mods = "Command"

[[keyboard.bindings]]
chars = "\u001B[6~\r"
key = "Down"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[96~\r"
key = "Down"
mods = "Alt"

[[keyboard.bindings]]
chars = "\u001B\u001B[96~\r"
key = "Down"
mods = "Command"

[[keyboard.bindings]]
chars = "\u001B[4h"
key = "Left"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[L"
key = "Left"
mods = "Alt"

[[keyboard.bindings]]
chars = "\u001B[@"
key = "Left"
mods = "Command"

[[keyboard.bindings]]
chars = "\u001B[4l"
key = "Right"
mods = "Shift"

[[keyboard.bindings]]
chars = "\u001B[K"
key = "Right"
mods = "Alt"

[[keyboard.bindings]]
chars = "#"
key = "Key3"
mods = "Alt"

[window]
title = "Alacritty NCDXT Laptop"

[window.dimensions]
columns = 132
lines = 43

[keyboard]
EOF
) > /tmp/alacritty-ncdxt-laptop.toml
/usr/local/bin/alacritty --config-file /tmp/alacritty-ncdxt-laptop.toml -e /usr/local/bin/ctelnet ${host} ${port}
