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
window:
  # Window dimensions (changes require restart)
  #
  # Number of lines/columns (not pixels) in the terminal. The number of columns
  # must be at least 2, while using a value of 0 for columns and lines will
  # fall back to the window manager-s recommended size.
  dimensions:
    columns: 132
    lines: 43

  # Window title
  title: Alacritty NCDXT Standard Keyboard

# Colors (based on Ethan Schoonover-s Solarized colour scheme)
colors:
  # Default colors
  primary:
    background: '#fdf6e3'
    foreground: '#586e75'

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
  duration: 50

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
  - { key: F1,          mods: Alt,                       chars: "\x1b[925~\x0d"    }
  - { key: F1,          mods: Control,                   chars: "\x1b[25~\x0d"     }
  - { key: F1,          mods: Shift,                     chars: "\x1b[911~\x0d"    }
  - { key: F1,                                           chars: "\x1b[11~\x0d"     }
  - { key: F2,          mods: Alt,                       chars: "\x1b[926~\x0d"    }
  - { key: F2,          mods: Control,                   chars: "\x1b[26~\x0d"     }
  - { key: F2,          mods: Shift,                     chars: "\x1b[912~\x0d"    }
  - { key: F2,                                           chars: "\x1b[12~\x0d"     }
  - { key: F3,          mods: Alt,                       chars: "\x1b[928~\x0d"    }
  - { key: F3,          mods: Control,                   chars: "\x1b[28~\x0d"     }
  - { key: F3,          mods: Shift,                     chars: "\x1b[913~\x0d"    }
  - { key: F3,                                           chars: "\x1b[13~\x0d"     }
  - { key: F4,          mods: Alt,                       chars: "\x1b[929~\x0d"    }
  - { key: F4,          mods: Control,                   chars: "\x1b[29~\x0d"     }
  - { key: F4,          mods: Shift,                     chars: "\x1b[914~\x0d"    }
  - { key: F4,                                           chars: "\x1b[14~\x0d"     }
  - { key: F5,          mods: Shift,                     chars: "\x1b[915~\x0d"    }
  - { key: F5,                                           chars: "\x1b[15~\x0d"     }
  - { key: F6,          mods: Shift,                     chars: "\x1b[917~\x0d"    }
  - { key: F6,                                           chars: "\x1b[17~\x0d"     }
  - { key: F7,          mods: Shift,                     chars: "\x1b[918~\x0d"    }
  - { key: F7,                                           chars: "\x1b[18~\x0d"     }
  - { key: F8,          mods: Shift,                     chars: "\x1b[919~\x0d"    }
  - { key: F8,                                           chars: "\x1b[19~\x0d"     }
  - { key: F9,          mods: Shift,                     chars: "\x1b[920~\x0d"    }
  - { key: F9,                                           chars: "\x1b[20~\x0d"     }
  - { key: F10,         mods: Shift,                     chars: "\x1b[921~\x0d"    }
  - { key: F10,                                          chars: "\x1b[21~\x0d"     }
  - { key: F11,         mods: Shift,                     chars: "\x1b[923~\x0d"    }
  - { key: F11,                                          chars: "\x1b[23~\x0d"     }
  - { key: F12,         mods: Shift,                     chars: "\x1b[924~\x0d"    }
  - { key: F12,                                          chars: "\x1b[24~\x0d"     }
  - { key: Home,                                         chars: "\x1b[H"           }
  - { key: PageUp,      mods: Control,                   chars: "\x1b\x1b[95~\x0d" }
  - { key: PageUp,      mods: Shift,                     chars: "\x1b[95~\x0d"     }
  - { key: PageUp,                                       chars: "\x1b[5~\x0d"      }
  - { key: End,         mods: Control,                   chars: "\x1b[K"           }
  - { key: End,                                          chars: "\x1b[4l"          }
  - { key: PageDown,    mods: Control,                   chars: "\x1b\x1b[96~\x0d" }
  - { key: PageDown,    mods: Shift,                     chars: "\x1b[96~\x0d"     }
  - { key: PageDown,                                     chars: "\x1b[6~\x0d"      } 
  - { key: Insert,      mods: Control,                   chars: "\x1b[@"           }
  - { key: Insert,      mods: Shift,                     chars: "\x1b[L"           }
  - { key: Insert,                                       chars: "\x1b[4h"          }
  - { key: Delete,      mods: Control,                   chars: "\x1b[P"           }
  - { key: Delete,      mods: Shift,                     chars: "\x1b[M"           }
  - { key: Delete,                                       chars: "\x1b[P"           }
EOF
) > /tmp/alacritty-ncdxt-desktop.yml
/usr/local/bin/alacritty --config-file /tmp/alacritty-ncdxt-desktop.yml -e /usr/local/bin/ctelnet ${host} ${port}
