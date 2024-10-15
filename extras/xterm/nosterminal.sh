#!/bin/bash
function show_help () {
    cat <<EOF

Usage: nosterminal.sh [-h] [host-ip-or-name [port-number]]

Run xterm with definitions that make it look like an NCD16/NCD19 
Xterminal with type ahead. This is primarily for use with the 
NOS 2.8.7 turnkey system which supports these terminals.

The X resources file included here and the matching NOS TDU 
definition are the work of Gerard van der Grinten. 

Note that this needs a full size (104/105 key) keyboard.
For laptop keyboards, an alternative is needed, such as iTerm2 
with an NCD profile on macOS.

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
!------------- Beginning of Unix file .Xdefaults for Cyber XTERM --------
!                                                 
! Define cyber2 VT100 prefix, use xrdb .Xdefaults  
!                                                 
! Note: You must allow the c pre-processor to run on this file.
!       Do NOT use the -nocpp option on the xrdb command.
!                                                 
!       To allow these key mappings to work, put them in a file on unix,
!       and execute the command:                  
!            xrdb whatever_filename_you_used      
!       Then invoke an xterm like this:           
!            xterm -name cyber2 -132 -j            
!       The '-name cyber2' specifies use of the cyber2 key mapping.
!       The '-132' specifies that switching to 132 column mode is allowed.
!       The '-j' specifies use of jump scrolling instead of smooth
!                scrolling (this is optional).    
!                                                 
#ifndef CR
#define CR string(0x0d)
#endif
#ifndef ESC
#define ESC string(0x1b)
#endif
#define SH_FKEY string(0x1b) string([9)
#ifndef PREFIX
#define PREFIX string(0x1b) string([)
#endif
#ifndef LF
#define LF string(0x0a)
#endif
cyber2*scrollBar:        on
cyber2*saveLines:        450
cyber2*borderWidth:      2
cyber2*font:             6x13
cyber2*boldFont:         6x13bold
cyber2*cursorColor:	red
cyber2*background:	NavyBlue
cyber2*foreground:	white
cyber2*loginShell:       true
cyber2*VT100.geometry:     80x43
cyber2*VT100.Translations:   #override\
 <Key>BackSpace:     string(0x08)\n\
     Alt<Key>F1:     SH_FKEY string(25~) CR \n\
    Ctrl<Key>F1:     PREFIX  string(25~) CR \n\
    Meta<Key>F1:                               \n\
  Shift <Key>F1:     SH_FKEY string(11~) CR \n\
        <Key>F1:     PREFIX  string(11~) CR \n\
     Alt<Key>F2:     SH_FKEY string(26~) CR \n\
    Ctrl<Key>F2:     PREFIX  string(26~) CR \n\
    Meta<Key>F2:                               \n\
  Shift <Key>F2:     SH_FKEY string(12~) CR \n\
        <Key>F2:     PREFIX  string(12~) CR \n\
     Alt<Key>F3:     SH_FKEY string(28~) CR \n\
    Ctrl<Key>F3:     PREFIX  string(28~) CR \n\
    Meta<Key>F3:                               \n\
  Shift <Key>F3:     SH_FKEY string(13~) CR \n\
        <Key>F3:     PREFIX  string(13~) CR \n\
     Alt<Key>F4:     SH_FKEY string(29~) CR \n\
    Ctrl<Key>F4:     PREFIX  string(29~) CR \n\
    Meta<Key>F4:                               \n\
  Shift <Key>F4:     SH_FKEY string(14~) CR \n\
        <Key>F4:     PREFIX  string(14~) CR \n\
     Alt<Key>F5:                               \n\
    Ctrl<Key>F5:                               \n\
    Meta<Key>F5:                               \n\
  Shift <Key>F5:     SH_FKEY string(15~) CR \n\
        <Key>F5:     PREFIX  string(15~) CR \n\
     Alt<Key>F6:                               \n\
    Ctrl<Key>F6:                               \n\
    Meta<Key>F6:                               \n\
  Shift <Key>F6:     SH_FKEY string(17~) CR \n\
        <Key>F6:     PREFIX  string(17~) CR \n\
     Alt<Key>F7:                               \n\
    Ctrl<Key>F7:                               \n\
    Meta<Key>F7:                               \n\
  Shift <Key>F7:     SH_FKEY string(18~) CR \n\
        <Key>F7:     PREFIX  string(18~) CR \n\
     Alt<Key>F8:                               \n\
    Ctrl<Key>F8:                               \n\
    Meta<Key>F8:                               \n\
  Shift <Key>F8:     SH_FKEY string(19~) CR \n\
        <Key>F8:     PREFIX  string(19~) CR \n\
     Alt<Key>F9:                               \n\
    Ctrl<Key>F9:                               \n\
    Meta<Key>F9:                               \n\
  Shift <Key>F9:     SH_FKEY string(20~) CR \n\
        <Key>F9:     PREFIX  string(20~) CR \n\
     Alt<Key>F10:                              \n\
    Ctrl<Key>F10:                              \n\
    Meta<Key>F10:                              \n\
  Shift <Key>F10:    SH_FKEY string(21~) CR \n\
        <Key>F10:    PREFIX  string(21~) CR \n\
     Alt<Key>F11:                              \n\
    Ctrl<Key>F11:                              \n\
    Meta<Key>F11:                              \n\
  Shift <Key>F11:    SH_FKEY string(23~) CR \n\
        <Key>F11:    PREFIX  string(23~) CR \n\
     Alt<Key>F12:                              \n\
    Ctrl<Key>F12:                              \n\
    Meta<Key>F12:                              \n\
  Shift <Key>F12:    SH_FKEY string(24~) CR \n\
        <Key>F12:    PREFIX  string(24~) CR \n\
        <Key>Home:   PREFIX  string(H)         \n\
     Alt<Key>Prior:                            \n\
    Ctrl<Key>Prior:  ESC SH_FKEY string(5~) CR \n\
    Meta<Key>Prior:                            \n\
   Shift<Key>Prior:  SH_FKEY string(5~)  CR \n\
        <Key>Prior:  PREFIX  string(5~)  CR \n\
     Alt<Key>End:                              \n\
    Ctrl<Key>End:    PREFIX  string(K)         \n\
    Meta<Key>End:                              \n\
   Shift<Key>End:                              \n\
        <Key>End:    PREFIX  string(4l)        \n\
     Alt<Key>Next:                             \n\
    Ctrl<Key>Next:   ESC SH_FKEY string(6~) CR \n\
    Meta<Key>Next:                             \n\
   Shift<Key>Next:   SH_FKEY string(6~)  CR \n\
        <Key>Next:   PREFIX  string(6~)  CR \n\
     Alt<Key>Insert:                           \n\
    Ctrl<Key>Insert: PREFIX  string(@)         \n\
    Meta<Key>Insert:                           \n\
   Shift<Key>Insert: PREFIX  string(L)         \n\
        <Key>Insert: PREFIX  string(4h)        \n\
     Alt<Key>Delete:                           \n\
    Ctrl<Key>Delete: PREFIX  string(P)         \n\
    Meta<Key>Delete:                           \n\
   Shift<Key>Delete: PREFIX  string(M)         \n\
        <Key>Delete: PREFIX  string(P)
!
!----------- End of Unix file .Xdefaults for CYBER2 -------------------------
EOF
) > /tmp/Xresources.cyber2
xrdb -merge /tmp/Xresources.cyber2
xterm -ut -T "NOS Terminal 132" -name cyber2 -132 -geometry 132x43 -j -e ctelnet ${host} ${port}
