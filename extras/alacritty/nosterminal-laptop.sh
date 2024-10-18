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
window:
  # Window dimensions (changes require restart)
  #
  # Number of lines/columns (not pixels) in the terminal. The number of columns
  # must be at least 2, while using a value of 0 for columns and lines will
  # fall back to the window manager's recommended size.
  dimensions:
    columns: 132
    lines: 43

  # Window title
  title: Alacritty NCDXT Laptop

# Font configuration
font:
  normal:
    family: Menlo
    style: Regular
    
  size: 12.0
  
# Colors (based on Ethan Schoonover's Solarized colour scheme -- or not)
colors:
  # Default colors
  primary:
    #background: '#fdf6e3'
    #foreground: '#586e75'
    background: '#003863'
    foreground: '#f0f0f0'

  cursor:
    text: CellBackground
    cursor: '#b58900'

# Bell
#
# The bell is rung every time the BEL control character is received.
# This is also used to warn when crossing from column 72 to 73 (or back to 71).
bell:
  animation: EaseOutExpo

  # Duration of the visual bell flash in milliseconds. A duration of 0 will
  # disable the visual bell animation.
  duration: 150

  # Visual bell animation color.
  color: '#ff1111'

cursor:
  # Cursor style
  style:
    shape: Block
    blinking: Off

  blink_interval: 250

# Key bindings
# NCD X terminal as understood by NOS 2.8.7 (thanks to Gerard van der Grinten)

key_bindings:
  - { key: Back,                                         chars: "\x08"             }
  - { key: F1,                                           chars: "\x1b[11~\x0d"     }
  - { key: F1,          mods: Shift,                     chars: "\x1b[911~\x0d"    }
  - { key: F1,          mods: Command,                   chars: "\x1b[J\x0d"       }
  - { key: F1,          mods: Alt,                       chars: "\x1b[H"           }
  - { key: F2,                                           chars: "\x1b[12~\x0d"     }
  - { key: F2,          mods: Shift,                     chars: "\x1b[912~\x0d"    }
  - { key: F2,          mods: Command,                   chars: "\x1b[M"           }
  - { key: F2,          mods: Alt,                       chars: "\x1b[P"           }
  - { key: F3,                                           chars: "\x1b[13~\x0d"     }
  - { key: F3,          mods: Shift,                     chars: "\x1b[913~\x0d"    }
  - { key: F3,          mods: Command,                   chars: "\x1b[28~\x0d"     }
  - { key: F3,          mods: Alt,                       chars: "\x1b[928~\x0d"    }
  - { key: F4,                                           chars: "\x1b[14~\x0d"     }
  - { key: F4,          mods: Shift,                     chars: "\x1b[914~\x0d"    }
  - { key: F4,          mods: Command,                   chars: "\x1b[29~\x0d"     }
  - { key: F4,          mods: Alt,                       chars: "\x1b[929~\x0d"    }
  - { key: F5,                                           chars: "\x1b[15~\x0d"     }
  - { key: F5,          mods: Shift,                     chars: "\x1b[915~\x0d"    }
  - { key: F6,                                           chars: "\x1b[17~\x0d"     }
  - { key: F6,          mods: Shift,                     chars: "\x1b[917~\x0d"    }
  - { key: F7,                                           chars: "\x1b[18~\x0d"     }
  - { key: F7,          mods: Shift,                     chars: "\x1b[918~\x0d"    }
  - { key: F8,                                           chars: "\x1b[19~\x0d"     }
  - { key: F8,          mods: Shift,                     chars: "\x1b[919~\x0d"    }
  - { key: F9,                                           chars: "\x1b[20~\x0d"     }
  - { key: F9,          mods: Shift,                     chars: "\x1b[920~\x0d"    }
  - { key: F10,                                          chars: "\x1b[21~\x0d"     }
  - { key: F10,         mods: Shift,                     chars: "\x1b[921~\x0d"    }
  - { key: F11,                                          chars: "\x1b[23~\x0d"     }
  - { key: F11,         mods: Shift,                     chars: "\x1b[923~\x0d"    }
  - { key: F12,                                          chars: "\x1b[24~\x0d"     }
  - { key: F12,         mods: Shift,                     chars: "\x1b[924~\x0d"    }
  - { key: Up,          mods: Shift,                     chars: "\x1b[5~\x0d"      }
  - { key: Up,          mods: Alt,                       chars: "\x1b[95~\x0d"     }
  - { key: Up,          mods: Command,                   chars: "\x1b\x1b[95~\x0d" }
  - { key: Down,        mods: Shift,                     chars: "\x1b[6~\x0d"      }
  - { key: Down,        mods: Alt,                       chars: "\x1b[96~\x0d"     }
  - { key: Down,        mods: Command,                   chars: "\x1b\x1b[96~\x0d" }
  - { key: Left,        mods: Shift,                     chars: "\x1b[4h"          }
  - { key: Left,        mods: Alt,                       chars: "\x1b[L"           }
  - { key: Left,        mods: Command,                   chars: "\x1b[@"           }
  - { key: Right,       mods: Shift,                     chars: "\x1b[4l"          }
  - { key: Right,       mods: Alt,                       chars: "\x1b[K"           }
  - { key: Key3,        mods: Alt,                       chars: "#"                }
EOF
) > /tmp/alacritty-ncdxt-laptop.yml
/usr/local/bin/alacritty --config-file /tmp/alacritty-ncdxt-laptop.yml -e /usr/local/bin/ctelnet ${host} ${port}
