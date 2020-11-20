#!/usr/bin/env python3
"""
gterm.py - A Telnet + OpenGL Terminal Emulator with Graphics and APL Capabilities.
==================================================================================
* We extend the standard Python Telnet class and implement a dumb terminal using PyQt and OpenGL. 
* Although the terminal is indeed dumb, the character glyphs are defined in an image file and 
  could, in principle, display any sort of representation for a 7 bit code point. 
* The mapping between keys and code points can also be changed at will and there are several 
  other features that make for a flexible environment for implementing 'unusual' command line
  interfaces to 'unusual' host systems.
* There is a vector graphics display capability which could easily be extended in all sorts of
  ways.
* There is a virtual keyboard facility currently used allow easy input of APL symbols.
* The default character glyphs also provide APL symbols (and many other 'scientific' characters).

What it does not do:
- There is no character cell addressability. I.e. it is like a teletype, not a VT100 etc.
- ANSI command strings are thrown away (cleanly) - except for our own graphics commands.

Original written in 2013 as a Python learning exercise.
- Modified 31-MAR-2017 for PyQt 5 compatibility.
- Modified April 2019 to get backspace behaviour to appear as expected today.
- Modified 23/24-MAY-2019 to add history recall and editing. Idiotic file transfer stuff removed.
- Modified 29/30-MAY-2019 to add graph plotting commands. Cairo rendering arguably improved.
- Converted to Python 3 26-NOV-2019. Also now uses PySide2 instead of PyQt5.
"""
# Imports ... Lots of them!
import sys
try:
    from OpenGL.GL import GL_ALPHA
    from OpenGL.GL import GL_BGRA
    from OpenGL.GL import GL_BLEND
    from OpenGL.GL import GL_CLAMP
    from OpenGL.GL import GL_COLOR_BUFFER_BIT
    from OpenGL.GL import GL_FLAT
    from OpenGL.GL import GL_LINEAR
    from OpenGL.GL import GL_LINEAR_MIPMAP_LINEAR
    from OpenGL.GL import GL_LINES
    from OpenGL.GL import GL_LUMINANCE
    from OpenGL.GL import GL_MODULATE
    from OpenGL.GL import GL_NEAREST
    from OpenGL.GL import GL_ONE_MINUS_SRC_ALPHA
    from OpenGL.GL import GL_POLYGON
    from OpenGL.GL import GL_PROJECTION
    from OpenGL.GL import GL_QUADS
    from OpenGL.GL import GL_RGB8
    from OpenGL.GL import GL_SRC_ALPHA
    from OpenGL.GL import GL_TEXTURE_2D
    from OpenGL.GL import GL_TEXTURE_ENV
    from OpenGL.GL import GL_TEXTURE_ENV_MODE
    from OpenGL.GL import GL_TEXTURE_MAG_FILTER
    from OpenGL.GL import GL_TEXTURE_MIN_FILTER
    from OpenGL.GL import GL_TEXTURE_WRAP_S
    from OpenGL.GL import GL_TEXTURE_WRAP_T
    from OpenGL.GL import GL_UNPACK_ALIGNMENT
    from OpenGL.GL import GL_UNSIGNED_BYTE
    from OpenGL.GL import GL_UNSIGNED_INT_8_8_8_8_REV
    from OpenGL.GL import glBegin
    from OpenGL.GL import glBindTexture
    from OpenGL.GL import glBlendFunc
    from OpenGL.GL import glClear
    from OpenGL.GL import glClearColor
    from OpenGL.GL import glColor4f
    from OpenGL.GL import glDisable
    from OpenGL.GL import glEnable
    from OpenGL.GL import glEnd
    from OpenGL.GL import glFlush
    from OpenGL.GL import glGenTextures
    from OpenGL.GL import glLineWidth
    from OpenGL.GL import glLoadIdentity
    from OpenGL.GL import glMatrixMode
    from OpenGL.GL import glOrtho
    from OpenGL.GL import glPixelStorei
    from OpenGL.GL import glRectf
    from OpenGL.GL import glShadeModel
    from OpenGL.GL import glTexCoord2f
    from OpenGL.GL import glTexEnvi
    from OpenGL.GL import glTexImage2D
    from OpenGL.GL import glTexParameterf
    from OpenGL.GL import glVertex2f
    from OpenGL.GL import glViewport
    
    from OpenGL.GLU import gluBuild2DMipmaps
except ImportError:
    print("GTerm needs PyOpenGL.")
    sys.exit(9)

try:
    from PySide2.QtCore import QCoreApplication
    from PySide2.QtCore import QEvent
    from PySide2.QtCore import QRect
    from PySide2.QtCore import Qt

    from PySide2.QtGui import QIcon

    from PySide2.QtWidgets import QApplication
    from PySide2.QtWidgets import QCheckBox
    from PySide2.QtWidgets import QComboBox
    from PySide2.QtWidgets import QDialog
    from PySide2.QtWidgets import QFileDialog
    from PySide2.QtWidgets import QHBoxLayout
    from PySide2.QtWidgets import QLabel
    from PySide2.QtWidgets import QLineEdit
    from PySide2.QtWidgets import QOpenGLWidget
    from PySide2.QtWidgets import QPushButton
    from PySide2.QtWidgets import QScrollArea
    from PySide2.QtWidgets import QSpinBox
    from PySide2.QtWidgets import QVBoxLayout
    from PySide2.QtWidgets import QWidget
    from PySide2.QtWidgets import QMessageBox

except ImportError:
    print("GTerm needs PySide2.")
    sys.exit(9)

try:
    from PIL import Image
except ImportError:
    print("GTerm needs Python Imaging Library.")
    sys.exit(9)
    
try:
    import numpy
except ImportError:
    print("GTerm needs Numpy.")
    sys.exit(9)
    
import optparse
import select
import socket
# Now here's a thing: import * below leaves constants undefined ...
from telnetlib import Telnet, DO, DONT, WILL, WONT, IAC, ECHO, SGA
import tty

try:
    import termios
except ImportError:
    print("GTerm needs termios.")
    sys.exit(9)
    
import threading
import time
import string
import json
import codecs
import os
import shutil
import math

try:
    import grid
except ImportError:
    print("GTerm needs grid.")
    sys.exit(9)
    
try:
    import cairo
except:
    print("GTerm needs cairo.")
    sys.exit(9)
    
try:
    import pyaudio
    import wave
except ImportError:
    print("GTerm needs PyAudio and Wave audio format.")
    sys.exit(9)

try:
    from githashvalue import _current_git_hash
except ImportError:
    _current_git_hash="0000000000000000000000000000000000000000"

try:
    from githashvalue import _current_git_desc
except ImportError:
    _current_git_desc="v?.?"

def negot(sock,cmd,opt):
    """
    Telnet option negotiation callback.
    Telling the server to DO suppress go ahead and echo if it wants to
    seems to be the minimum necessary for sane behaviour.
    """
    #print 'cmd:',repr(cmd),' opt:',repr(opt)
    if cmd in (DO, DONT):
        sock.sendall(IAC + WONT + opt)
    elif cmd in (WILL, WONT):
        # DO: Suppress go ahead, echo.
        if cmd == WILL and ( opt == SGA or opt == ECHO ):
            sock.sendall(IAC + DO + opt )
        else:
            sock.sendall(IAC + DONT + opt)

def _strtobytes( py3string ):
    """
    Convert a Python3 string to UTF-8 bytes to pass as c_char_p to C functions.
    For strings that should be so passed, this will result in 8 bit bytes, which
    is as required. For other (Unicode) strings ... tough luck.
    """
    if py3string is None:
        return None
    else:
        return py3string.encode('utf-8')

def _bytestostr( ccharpin ):
    """
    Convert an array of 8 bit bytes, such as may be returned from C code
    using c_char_p arguments, to a string.
    """
    if ccharpin is None:
        return None
    else:
        return ccharpin.decode('utf-8')

def _strtobytes_ifnot( py3string ):
    """
    If py3string is NOT already bytes, make it so.
    """
    if type(py3string) is bytes:
        return py3string
    else:
        return _strtobytes(py3string)

def _bytestostr_ifnot( ccharpin ):
    """
    If ccharpin is NOT already a (wide) string, make it so.
    """
    if type(ccharpin) is str:
        return ccharpin
    else:
        return _bytestostr(ccharpin)            

#################
# XTelnet CLASS #
#################

class XTelnet(Telnet,object):
    """
    Override some Telnet class methods and add some others to create
    a more useful version. Specifically:
    - interact() sends \r\n at line end rather than just \n because many hosts
      never get any data otherwise (Unix might - VMS and NOS definitely do not).
    - interact_ch() performs character-at-a-time interaction, which is much
      more useful than line-at-a-time (usually). Most systems (default, anyway)
      echo characters (full duplex) which gives unwanted results with line-at-a-time.
    - interact_ch_input() does blocking reads only from the server.
    """

    def __init__(self, host=None, port=0, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        super(XTelnet,self).__init__(host,port,timeout)
        self.rawmode = False
        self.old_settings = None
        self.eof_func = None
        self.received_function = None
        self.set_option_negotiation_callback(negot)

    def __del__(self):
        """
        Destructor -- close the connection.
        """
        try:
            if self.rawmode:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.old_settings)
        except:
            pass
        self.close()

    def set_eof_func(self,func):
        """
        Set a function to call when the remote server closes the connection.
        """
        self.eof_func = func

    def interact(self):
        """
        Interaction function, emulates a very dumb telnet client.
        """
        if sys.platform == "win32":
            self.mt_interact()
            return
        while 1:
            rfd, wfd, xfd = select.select([self, sys.stdin], [], [])
            if self in rfd:
                try:
                    text = self.read_eager()
                except EOFError:
                    if self.eof_func != None:
                        self.eof_func()
                    break
                if text:
                    sys.stdout.write(text)
                    sys.stdout.flush()
            if sys.stdin in rfd:
                line = sys.stdin.readline()
                if not line:
                    break
                line = line.replace('\n','\r\n') # NG: Otherwise no host I've tried gets any data.
                self.write(line)

    def interact_ch(self):
        """
        Interaction function, emulates a (not so) very dumb telnet client.
        This does things one character at a time. Which is usually the best way.
        Only for Linux.
        """
        if sys.platform == "win32":
            return
        # Set up for immediate, single character, keyboard input.
        fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(fd)
        tty.setraw(fd)
        self.rawmode = True
        # Loop until remote server closes the connection.
        while 1:
            # Block until either server sends a character or user types on keyboard.
            rfd, wfd, xfd = select.select([self, sys.stdin], [], [])
            # Server sent character.
            if self in rfd:
                try:
                    text = self.read_eager()
                except EOFError:
                    if self.eof_func != None:
                        self.eof_func()
                    break
                if text:
                    sys.stdout.write(text)
                    sys.stdout.flush()
            # User typed character.
            if sys.stdin in rfd:
                getch = sys.stdin.read(1)
                if not getch:
                    break
                # Make sure <return> (key) actually sends <CR><LF> as Telnet defines it should.
                if getch == '\r':
                    self.write('\r\n')
                else:
                    self.write(getch)

    def set_data_received_function(self,data_received):
        '''
        Set function to call when data is received from the server.
        '''
        self.received_function = data_received
        
    def interact_ch_input(self):
        """
        Wait for input from the server end of the Telnet connection only.
        """
        if sys.platform == "win32":
            return
        while 1:
            try:
                rfd, wfd, xfd = select.select([self], [], [])
            except OSError:
                return # Something using XTelnet has probably closed the connection. Ugly, but ...
            if self in rfd:
                try:
                    text = self.read_eager()
                except EOFError:
                    if self.eof_func != None:
                        self.eof_func()
                    break
                if text:
                    if self.received_function != None:
                        self.received_function(text)
                    else:
                        sys.stdout.write(text)
                        sys.stdout.flush()


####################
# GLOBAL FUNCTIONS #
####################

def eof_func():
    """
    Example function to call when session is closed.
    """
    print('\n*** Connection closed by remote host ***\r\n')    

def main_terminal_telnet():
    """
    Simple, but pretty much fully functional, telnet client using Terminal
    application on host (and keyboard). I.e. run this from a Terminal window.
    """
    usage = "./gty.py -h host_name -p port_number"

    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-a", "--address", dest="address", default="localhost")
    parser.add_option("-p", "--port", dest="port", default=23)

    (options,args) = parser.parse_args()

    try:
        session = XTelnet(options.address, options.port)
    except:
        print('telnetlib error: could not connect to ', options.address, ' ', options.port)
    else:
        #session.set_debuglevel(10)
        session.interact_ch()

def readchar():
    """
    Read a single character from the keyboard immediately. Do not wait for end-of-line.
    """
    try:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    except:
        return 0

def readchar_thread(session,junk):
    """
    Read characters from the keyboard indefinitely. Send each one to the Telnet server.
    """
    while 1:
        getch = readchar()
        if not getch:
            break
        # Make sure <return> (key) actually sends <CR><LF> as Telnet defines it should.
        if getch == '\r':
            session.write('\r\n')
        else:
            session.write(getch)

def readserver_thread(session,junk):
    """
    Run the Telnet session input (from server) handler in a separate thread.
    """
    session.interact_ch_input()

def received_data_func(text):
    """
    Do something with the data received from the server. Such as display it!
    Note that this will usually get a single character per call.
    """
    sys.stdout.write(text)
    sys.stdout.flush()

def main_sep_terminal_telnet():
    """
    Another version of the simple Telnet client which uses threads to run the keyboard input
    and screen output halves of the connection independently and asynchronously. This sort of
    approach should be compatible with GUI based Telnet clients. With luck.
    """
    usage = "./gty.py -h host_name -p port_number"

    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-a", "--address", dest="address", default="localhost")
    parser.add_option("-p", "--port", dest="port", default=23)

    (options,args) = parser.parse_args()

    try:
        session = XTelnet(options.address, options.port)
    except:
        print('telnetlib error: could not connect to ', options.address, ' ', options.port)
    else:
        #session.set_debuglevel(10)
        # Establish keyboard input and screen output functions.
        session.set_eof_func(eof_func)
        session.set_data_received_function(received_data_func)
        # Prepare to reset the terminal state after single character input is over.
        old_term_settings = termios.tcgetattr(sys.stdin.fileno())
        # Create and start two threads: one handling keyboard input and sending characters
        # to the remote Telnet server, and another handing characters received from the
        # remote Telnet server and writing them on the screen.
        kbd_thread = threading.Thread(target=readchar_thread, args=(session,0))
        scr_thread = threading.Thread(target=readserver_thread, args=(session,0))
        kbd_thread.start()
        scr_thread.start()
        # Wait for the remote server to close the Telnet connection.
        print("Session started. Mainline waiting for server to close connection...")
        scr_thread.join()
        # Restore sanity to the terminal after single character input.
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_term_settings)
        print("Session done ... Type <return> to exit.")
        # This is a not so nice trick to get the readchar_thread to actually exit.
        # Killing a thread is apparently too horrible to contemplate (more nonsense).
        sys.stdin.close()
        readchar()

def get_application_file_name( appname, filename, exttest=None ):
    """
    Return filename prefixed with a directory path appropriate to the OS.
    If the expected filedoes not exist, return prefixed by the current directory.
    """
    if sys.platform.startswith('darwin'):
        appdir = '/Applications/{0}.app/Contents/MacOS'.format(appname)
    else:
        appdir = '/usr/local/applications/{0}'.format(appname)
    loc = os.path.join(appdir,filename)
    if exttest is not None:
        testloc = loc + exttest
    else:
        testloc = loc
    if not os.path.isfile(testloc):
        return os.path.join('./',filename)
    else:
        return loc


############################
#    GTerm Widget CLASS    #
#   Glass teletype using   #
# PyQt 5 and QOpenGLWidget #
############################

class GTermWidget(QOpenGLWidget):
    """
    Implements a simple glass teletype style keyboard and screen using
    OpenGL to draw characters as texture mapped rectangles. The characters
    are defined in an image file. As it stands, this class just echoes on the
    screen whatever is typed on the keyboard. Classes inheriting from this can
    do more useful things - such as telnet and serial connections to other systems.
    """
    def __init__(self, charsetname='unknown',vkbname='unknown',umapname='unknown',parent = None):
        super(GTermWidget, self).__init__(parent)
        self.save_charsetname = charsetname
        self.save_vkbname = vkbname
        self.save_umapname = umapname
        self.icharnum = 5
        self.debuglevel = 0
        self.shownonprint = False
        self.ffclears = False
        self.papermode = False
        self.newlinesin = 0
        self.userwidget = None
        # Modifier key states.
        self.ctrl = False
        self.shift = False
        self.shiftlock = False
        self.alt = False
        # Character remapping dictionaries.
        # These allow any single character to be mapped to any other.
        self.incharmap = {}
        self.outcharmap = {}
        # Fancy keyboard key mapping dictionary.
        # This allows a keyboard keycode to be mapped to a string.
        self.fancykeymap = {}
        # The display screen.
        self.line = []
        self.screen = []
        self.xmargin = 20
        self.ymargin = 20
        self.maxlines = 1040 # In scroll buffer.
        self.width_pixels = 800 # Initial drawing area size.
        self.height_pixels = 700
        self.aspect = float(self.height_pixels) / float(self.width_pixels)
        self.scroll = 0
        # Mouse position tracking.
        self.oldmouse_x = 0
        self.oldmouse_y = 0
        # Read character to texture location data, then read the texture
        # image containing the character glyphs.
        ourchardata = get_application_file_name( 'gterm', charsetname, exttest='.jsn' )
        self.loadCharDefinitions(ourchardata)
        self.visiblelines = self.height_pixels // self.linespace + 1
        self.visiblechars = self.width_pixels // self.charspace + 1
        # Read any virtual keyboard definition.
        self.vkb_have = False
        self.vkb_tooltip = False
        if vkbname != 'none':
            ourvkbdata = get_application_file_name( 'gterm', vkbname, exttest='.jsn' )
            self.loadVkbDefinitions(ourvkbdata)
            self.vkb_down_keynum = -1
        # Create a lock to serialize access to screen data.
        self.screenlock = threading.Lock()
        self.changed = 0
        # Keep track of the length of the last line.
        self.prevlen = 0
        self.tabpos = 0
        self.tabstop = 8
        # Escape sequence tracking (input)
        self.escapeProcessFuncList = []
        self.escapeProcessFunc = None
        self.escapeChar = '\033'
        self.escapeseq = []
        self.inescape = False
        self.numescape = 0
        self.grafescape = False
        self.do_not_process_escapes = False
        # Widget state.
        self.setMinimumSize(self.width_pixels,self.height_pixels)
        self.setFocusPolicy(Qt.ClickFocus)
        self.havefocus = False
        self.haveconnection = False
        self.vkb_show = False
        self.viewport = (self.width_pixels,self.height_pixels)
        # Logging in Unicode. Read in the mapping between our character numbers
        # and the best equivalent Unicode character point.
        self.flog = None
        self.unicode_map = None
        if umapname != 'none':
            ourumapname = get_application_file_name( 'gterm', umapname, exttest='.jsn' )
            self.loadUnicodeMap(ourumapname)
        # Graphics commands and state.
        self.gcb = []
        self.drawgraf = False
        self.gcblock = threading.Lock()
        self.gchanged = 0
        self.gcbcmds = 0
        # Bell sound.
        self.bell_wav = get_application_file_name( 'gterm', 'beep-3.wav' )
        # Ensure control key is still control key (not CMD key) on MacOS. (MAY 2019).
        # Also need to know if MacOS to get hash key.
        self.iam_macos = sys.platform.startswith('darwin')
        if self.iam_macos:
            self.QtControlKeyCode = Qt.Key_Meta
        else:
            self.QtControlKeyCode = Qt.Key_Control
        # Improved NOS APL 2 backspace behaviour.
        self.newline_after_backspace = False
        self.suppress_next_newline_display = False
        # Cursor character position offset for current line editing.
        self.cursor_char_offset = 0
        # Horizontal guide positions.
        self.h_guide_positions = []

    def loadCharData(self,jsonfile):
        """
        Load the locations of each character in the character texture from
        a JSON format file containing a single dictionary. I don't much like
        JSON, but it sort of works for this while being human readable.
        The single dictionary also contains character metrics.
        """
        try:
            flun = open(jsonfile,'r')
            input_dir = json.load(flun)
            flun.close()
            self.chardict = {}
            metricdict = {}
            for k in input_dir:
                try:
                    ikey = int(k)
                    self.chardict[ikey] = input_dir[k]
                except ValueError:
                    metricdict[k] = input_dir[k]
            self.scale = 1
            self.charwidth = metricdict['charwidth']
            self.charheight = metricdict['charheight']
            self.charspace = self.charwidth+1
            self.linespace = self.charheight+1
            self.cellduv = metricdict['cellduv']
            self.dsu = self.cellduv[0]
            self.dsv = self.cellduv[1]
        except:
            print('**** Failed to open or parse font data file! Giving up!')
            sys.exit(1)

    def loadCharImage(self,pngfile):
        """
        Open a PNG image file containing the character glyphs.
        """
        try:
            img = Image.open(pngfile)
            self.imgl = img.convert('L')
        except:
            print('**** Failed to open font texture image file! Giving up!')
            sys.exit(1)

    def loadCharDefinitions(self,charsetname):
        """
        Load the contents of the two files that define a character set.
        """
        if self.debuglevel > 1:
            print('Loading char data:', charsetname)
        self.loadCharData(str(charsetname)+'.jsn')
        self.loadCharImage(str(charsetname)+'.png')

    def loadVkbData(self,jsonfile):
        """
        Load information about the virtual keyboard, including the key number
        to character code map.
        """
        try:
            flun = open(jsonfile,'r')
            input_keydata = json.load(flun)
            flun.close()
            self.vkb_keymap = {}
            inputkeyposmap = input_keydata['keyposmap']
            for k in inputkeyposmap:
                try:
                    ikey = int(k)
                    self.vkb_keymap[ikey] = inputkeyposmap[k]
                except:
                    pass
            self.vkb_keycols = input_keydata['keycols']
            self.vkb_keyrows = input_keydata['keyrows']
            self.vkb_keyxdelta = input_keydata['keyxdelta']
            self.vkb_keyydelta = input_keydata['keyydelta']
            self.vkb_have = True
            if self.debuglevel > 1:
                print(self.vkb_keymap)
        except:
            self.vkb_have = False
            print('**** Failed to read virtual keyboard definition file. Giving up!')
            sys.exit(1)
        if self.debuglevel > 1:
            print(self.vkb_keymap)

    def loadVkbImage(self,pngfile):
        """
        Open a PNG image file containing a virtual keyboard image.
        """
        try:
            img = Image.open(pngfile)
            self.vkb_img = img.convert('L')
        except:
            print('**** Failed to open virtual keyboard image file! Giving up!')
            sys.exit(1)

    def loadVkbDefinitions(self,vkbname):
        """
        Load the contents of the two files that define a virtual keyboard.
        """
        if self.debuglevel > 1:
            print('Loading vkb data:', vkbname)
        self.loadVkbData(str(vkbname)+'.jsn')
        self.loadVkbImage(str(vkbname)+'.png')

    def loadUnicodeMap(self,mapname):
        """
        Load the mapping from our character numbers to Unicode char points.
        """
        mapfilename = str(mapname)+'.jsn'
        try:
            flun = open(mapfilename,'r')
            input_dir = json.load(flun)
            flun.close()
            self.unicode_map = {}
            for k in input_dir:
                try:
                    ikey = int(k)
                    self.unicode_map[ikey] = bytes(input_dir[k],encoding='utf-8').decode('unicode-escape')
                except:
                    pass
        except:
            print('**** Failed to open or parse Unicode map data file! Giving up!')
            sys.exit(1)

    def getBackgroundColour(self):
        """
        Find the background colour from havefocus and haveconnection.
        """
        if self.papermode:
            if self.havefocus:
                if self.haveconnection:
                    return (0.4,0.6,0.4,1.0)
                else:
                    return (0.6,0.4,0.4,1.0)
            else:
                if self.haveconnection:
                    return (0.05,0.3,0.05,1.0)
                else:
                    return (0.3,0.05,0.05,1.0)
        else:
            if self.havefocus:
                if self.haveconnection:
                    return (0.1,0.1,0.8,1.0)
                else:
                    return (0.8,0.1,0.1,1.0)
            else:
                if self.haveconnection:
                    return (0.05,0.05,0.3,1.0)
                else:
                    return (0.3,0.05,0.05,1.0)

    def getAltBackgroundColour(self):
        """
        Get the alternate background colour for "paper" mode. This is white/grey.
        """
        if self.havefocus:
            return (0.8,0.8,0.8,1.0)
        else:
            return (0.2,0.2,0.2,1.0)

    def getForegroundColour(self):
        """
        Return the foreground colour.
        """
        if self.papermode:
            return (0.0,0.0,0.0,1.0)
        else:
            return (1.0,1.0,1.0,1.0)

    def getCursorColour(self):
        """
        Return the cursor colour.
        """
        return (0.9,0.1,0.1,1.0)

    def set_debuglevel(self,deblev):
        """
        Set debug level. 0 turns off all debug. 1 and 2 are used currently.
        """
        self.debuglevel = deblev

    def set_shownonprint(self,shownonprint):
        """
        Display non-printing characters (or not).
        """
        self.shownonprint = shownonprint

    def set_showvkb(self,showvkb):
        """
        Display virtual keyboard (or not).
        """
        self.vkb_show = showvkb
        self.update()

    def set_userwidget(self,userobj):
        """
        Set what is using this widget.
        """
        self.userwidget = userobj

    def drawTexChar(self,charcode,xpos,ypos):
        """
        Draw character ucharcode at (xpos,yos).
        """
        # Find the right texture coordinate (top left of character) in pixels.
        try:
            (u,v) = self.chardict[charcode]
        except:
            (u,v) = (0.0,0.0)
        # Draw the rectangle.
        glBegin(GL_QUADS)
        glTexCoord2f(u,v)
        glVertex2f(xpos,ypos)
        glTexCoord2f(u+self.dsu, v)
        glVertex2f(xpos+self.charwidth,ypos)
        glTexCoord2f(u+self.dsu,v+self.dsv)
        glVertex2f(xpos+self.charwidth,ypos-self.charheight)
        glTexCoord2f(u,v+self.dsv)
        glVertex2f(xpos,ypos-self.charheight)
        glEnd()

    def draw_string(self,where,string):
        """
        Draw a string at an arbitrary position. Colour is as specified previously.
        """
        xpos = int(where[0])
        ypos = int(where[1])
        glBindTexture(GL_TEXTURE_2D,self.texture)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        for i in range(0,len(string)):
            self.drawTexChar(ord(string[i]),xpos,ypos)
            xpos += self.charspace
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)

    def draw_tip(self,where,string,leftpos=False):
        """
        Draw the tip text for this keyboard key.
        """
        if leftpos:
            xpos = int(where[0])
        else:
            xpos = int(where[0]) - (len(string) * self.charspace)
        ypos = int(where[1])
        # Grey background.
        glColor4f(0.3,0.3,0.3,1.0)
        glBegin(GL_QUADS)
        glVertex2f(xpos-3,ypos+3)
        glVertex2f(xpos+len(string)*self.charspace+6,ypos+3)
        glVertex2f(xpos+len(string)*self.charspace+6,ypos-self.charheight-3)
        glVertex2f(xpos-3,ypos-self.charheight-3)
        glEnd()
        # Yellow text
        glColor4f(1.0,1.0,0.0,1.0)
        self.draw_string((xpos,ypos),string)

    def set_cursor_char_offset(self,coffset):
        """
        Set the cursor offset from the end of line in characters.
        """
        self.cursor_char_offset = coffset

    def paintGL(self):
        """
        Draw all the characters on the screen, or interpret and draw the
        contents of the graphics command buffer.
        """
        # Graphics drawing.
        if self.drawgraf:
            if self.debuglevel > 2:
                print('paintGL(): drawgraf starts ...')
            to_x_pixels = self.viewport[0]
            to_y_pixels = self.aspect * to_x_pixels
            if self.debuglevel > 2:
                print("to_x_pixels=",to_x_pixels," to_y_pixels=",to_y_pixels," aspect=",self.aspect)

            # If there are no graphics commands, draw info string.
            if self.gcbcmds == 0:
                nodata = 'No graphics data.'
                glColor4f(1.0,0.0,0.0,1.0)
                self.draw_string(((self.viewport[0]-self.charspace*len(nodata))//2,\
                                   (self.viewport[1]-self.linespace)//2),nodata)
                
            # Have some commands in the graphics command buffer ...
            else:
                self.cairoRenderGraphicsToTexture(self.width_pixels,self.height_pixels)
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D,self.crgraf_texture)
                glColor4f(1,1,1,1)
                glBegin(GL_QUADS)
                glTexCoord2f(0.0,1.0)
                glVertex2f(0.0,0.0)
                glTexCoord2f(1.0, 1.0)
                glVertex2f(self.width_pixels,0.0)
                glTexCoord2f(1.0,0.0)
                glVertex2f(self.width_pixels,self.height_pixels)
                glTexCoord2f(0.0,0.0)
                glVertex2f(0.0,self.height_pixels)
                glEnd()
                glDisable(GL_TEXTURE_2D)
                    
        # Text drawing.
        else:
            # Colour the background
            # We need four background colours: Focus yes/no, Connected yes/no.
            if self.papermode:
                back_cols = (self.getBackgroundColour(), self.getAltBackgroundColour())
                ypos = -13.0
                for y in range(0,self.visiblelines,2):
                    back_col = back_cols[(self.newlinesin+self.scroll) & 1]
                    glColor4f(back_col[0], back_col[1], back_col[2], back_col[3])
                    glRectf(0.0,ypos,self.viewport[0],ypos+self.linespace)
                    ypos += self.linespace
                    back_col = back_cols[(self.newlinesin+self.scroll+1) & 1]
                    glColor4f(back_col[0], back_col[1], back_col[2], back_col[3])
                    glRectf(0.0,ypos,self.viewport[0],ypos+self.linespace)
                    ypos += self.linespace
            else:
                back_col = self.getBackgroundColour()
                glClearColor(back_col[0], back_col[1], back_col[2], back_col[3])
                glClear(GL_COLOR_BUFFER_BIT)
                # Draw horizontal guides (if any).
                for guidex in self.h_guide_positions:
                    xg = self.xmargin + guidex * self.charspace
                    glColor4f(0.0,0.0,0.0,1.0)
                    glLineWidth(2)
                    glBegin(GL_LINES)
                    glVertex2f(xg,0.0)
                    glVertex2f(xg,self.viewport[1])
                    glEnd()
                    glLineWidth(1)
            # Draw the characters blended over the background colour.
            fore_col = self.getForegroundColour()
            glColor4f(fore_col[0],fore_col[1],fore_col[2],fore_col[3])
            glBindTexture(GL_TEXTURE_2D,self.texture)
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            # Draw the previous screen lines.
            self.screenlock.acquire()
            lines = len(self.screen)
            firstvisible = lines - self.visiblelines - self.scroll
            if firstvisible < 0:
                firstvisible = 0
            lastvisible = lines - self.scroll
            if lastvisible < 0:
                lastvisible = 0
            if self.debuglevel > 2:
                print("Scrolling visible lines: visible ",self.visiblelines,"first visible",firstvisible)
            for j in range(firstvisible,lastvisible):
                xpos = self.xmargin
                ypos = self.linespace*(lastvisible-j)+self.ymargin
                for i in range(0,len(self.screen[j])):
                    self.drawTexChar(self.screen[j][i],xpos,ypos)
                    xpos += self.charspace
            # Draw the current line.
            xpos = self.xmargin
            ypos = self.ymargin
            if self.scroll == 0:
                for i in range(0,len(self.line)):
                    self.drawTexChar(self.line[i],xpos,ypos)
                    xpos += self.charspace
            else:
                self.draw_tip( (xpos,ypos),"... scrolled {0} ...".format(self.scroll), True)
            self.screenlock.release()
            # Turn off blending and texturing.
            glDisable(GL_BLEND)
            glDisable(GL_TEXTURE_2D)
            # Draw the cursor.
            curs_xpos = min( xpos, max( self.xmargin, xpos - self.cursor_char_offset * self.charspace ) )
            curs_col = self.getCursorColour()
            curs_dx = 0
            glColor4f(curs_col[0],curs_col[1],curs_col[2],curs_col[3])
            glBegin(GL_POLYGON)
            glVertex2f(curs_xpos+curs_dx,0)
            glVertex2f(curs_xpos+curs_dx+1,0)
            glVertex2f(curs_xpos+curs_dx+1,self.ymargin)
            glVertex2f(curs_xpos+curs_dx,self.ymargin)
            glEnd()
            # Virtual keyboard image.
            if self.vkb_have and self.vkb_show:
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D,self.vkb_texture)
                glColor4f(1,1,1,1)
                glBegin(GL_QUADS)
                glTexCoord2f(0.0,1.0)
                glVertex2f(self.viewport[0]-self.vkb_img.size[0],self.viewport[1]-self.vkb_img.size[1])
                glTexCoord2f(1.0, 1.0)
                glVertex2f(self.viewport[0],self.viewport[1]-self.vkb_img.size[1])
                glTexCoord2f(1.0,0.0)
                glVertex2f(self.viewport[0],self.viewport[1])
                glTexCoord2f(0.0,0.0)
                glVertex2f(self.viewport[0]-self.vkb_img.size[0],self.viewport[1])
                glEnd()
                glDisable(GL_TEXTURE_2D)
                # Key shading if down
                if self.vkb_down_keynum >= 0:
                    if self.vkb_tooltip:
                        glColor4f(1.0,1.0,0.0,0.3) # Tool tip yellow
                    else:
                        glColor4f(1.0,0.0,0.0,0.3) # Action red
                    keycenterpos_upside_down = self.vkb_key_to_screen_pos(self.vkb_down_keynum)
                    keycenterpos = (keycenterpos_upside_down[0],self.viewport[1] -
                                    keycenterpos_upside_down[1])
                    halfdx = self.vkb_keyxdelta*0.5
                    halfdy = self.vkb_keyydelta*0.5
                    glEnable(GL_BLEND)
                    glBegin(GL_QUADS)
                    glVertex2f(keycenterpos[0]-halfdx,keycenterpos[1]-halfdy)
                    glVertex2f(keycenterpos[0]+halfdx+1,keycenterpos[1]-halfdy)
                    glVertex2f(keycenterpos[0]+halfdx+1,keycenterpos[1]+halfdy)
                    glVertex2f(keycenterpos[0]-halfdx,keycenterpos[1]+halfdy)
                    glEnd()
                    glDisable(GL_BLEND)
                    # Tool tip mode (right mouse button)
                    if self.vkb_tooltip:
                        self.draw_tip(keycenterpos,self.vkb_keymap[self.vkb_down_keynum][1])
            # Graphics info.
            if self.gcbcmds > 0:
                sgi = 'GC:{0}'.format(self.gcbcmds)
                self.draw_tip((self.viewport[0],self.linespace),sgi)
        glFlush()

    def resizeGL(self, w, h):
        """
        Handle widget resizes.
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.scale*w, 0, self.scale*h, -50.0, 50.0)
        glViewport(0, 0, w, h)
        self.viewport = (w,h)
        self.width_pixels = w
        self.height_pixels = h
        self.aspect = float(self.height_pixels)/float(self.width_pixels)
        self.visiblelines = self.height_pixels // self.linespace + 1
        self.visiblechars = self.width_pixels // self.charspace + 1

    def initializeGL(self):
        """
        Initialize OpenGL for our task.
        """
        # Make an *alpha* texture from the *luminance* image data.
        img_data = numpy.asarray(self.imgl,dtype=numpy.uint8)
        self.texture = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glBindTexture(GL_TEXTURE_2D,self.texture)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP )
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP )
        # Generate textures. 
        if True:
            # Nearest neighbour minification sampling with a carefully pre-scaled texture.
            # This seems to give *by far* the best results (perhaps not surprisingly).
            glTexImage2D(GL_TEXTURE_2D, 0, GL_ALPHA, self.imgl.size[0], self.imgl.size[1], \
                             0, GL_ALPHA, GL_UNSIGNED_BYTE, img_data)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST )
        else:
            # Use MipMaps with arbitrary sized textures. Unfortunately, the best filtering 
            # OpenGL offers is nowhere near good enough for this application.
            gluBuild2DMipmaps(GL_TEXTURE_2D, GL_ALPHA, self.imgl.size[0], self.imgl.size[1], \
                                  GL_ALPHA, GL_UNSIGNED_BYTE, img_data)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR )
        glShadeModel(GL_FLAT)
        # You *must* turn on blending to get the desired result with the texture BTW!
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE )
        # And the virtual keyboard texture, if we have one.
        if self.vkb_have:
            self.vkb_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D,self.vkb_texture)
            vkb_data = numpy.asarray(self.vkb_img,dtype=numpy.uint8)
            glPixelStorei(GL_UNPACK_ALIGNMENT,1)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP )
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP )
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST )
            glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.vkb_img.size[0], self.vkb_img.size[1], \
                             0, GL_LUMINANCE, GL_UNSIGNED_BYTE, vkb_data)

    def screenDoNewLine(self):
        """
        Screen: Process a newline. I.e. go to a newline.
        """
        if self.debuglevel > 1:
            print('DoNewLine')
        self.screenlock.acquire()
        # Pop off lines that have gone off the top of the page.
        self.screen.append(self.line)
        if len(self.screen) > (self.maxlines-1):
            self.screen.pop(0)
        # If there is a log file, write to it.
        if self.flog != None:
            self.writeLogFile(self.line)
        # Empty the current line.
        self.line = []
        if self.debuglevel > 1:
            print('--> prevlen',self.prevlen)
        # If we were not at the beginning of the line, insert spaces to where we were.
        if self.prevlen > 0:
            for ispace in range(0,self.prevlen):
                self.line.append(32)
        self.changed = 2
        # Do not reset the character position on the line!
        #self.prevlen = 0
        #self.tabpos = 0
        self.newlinesin += 1 # Count total newlines for paper mode.
        self.screenlock.release()
        if self.debuglevel > 1:
            print('-- --> prevlen',self.prevlen)
        self.doUpdate(2)

    def screenDoReturnCarriage(self):
        """
        Screen: Process a carriage return. I.e. go to start of current line.
        """
        if self.debuglevel > 1:
            print('DoReturnCarriage')
        self.prevlen = 0
        self.tabpos = 0
        if self.debuglevel > 2:
            print('--> prevlen',self.prevlen)

    def screenClearLine(self,doupdate=False):
        """
        Screen: Empty the current line.
        """
        if self.debuglevel > 1:
            print('ClearLine')
        self.screenDoReturnCarriage()
        self.screenlock.acquire()
        self.line = []
        self.screenlock.release()
        if doupdate:
            self.doUpdate(27)

    def screenDoBackspace(self):
        """
        Screen: Process a backspace.
        """
        if self.debuglevel > 1:
            print('DoBackspace')
        self.screenlock.acquire()
        if( len(self.line) > 0 ):
            self.line.pop()
        self.prevlen -= 1
        if self.prevlen < 0:
            self.prevlen = 0
        self.changed = 2
        self.screenlock.release()
        if self.debuglevel > 2:
            print('--> prevlen',self.prevlen)
        self.doUpdate(3)

    def screenDoTab(self):
        """
        Screen: Process a horizontal tab.
        """
        if self.debuglevel > 1:
            print('DoTab')
        self.screenlock.acquire()
        nextpos = (int(self.prevlen/self.tabstop)+1) * self.tabstop
        numspaces = nextpos - self.prevlen
        for ispace in range(0,numspaces):
            self.line.append(32)
        self.screenlock.release()
        self.doUpdate(9)

    def screenDoFormFeed(self):
        """
        Screen: Process a form feed.
        """
        if self.debuglevel > 1:
            print('DoFormFeed')
        if self.ffclears:
            # Clear the screen on FF mode.
            self.screenlock.acquire()
            self.line = []
            self.screen = []
            self.changed = 2
            self.screenlock.release()
            self.doUpdate(15)
        else:
            # Output a printed page break string mode.
            ffstring = '-----<FF>---------------------------------------------------------'
            l = len(ffstring)
            for i in range(0,l):
                self.screenAddCharSimple(ord(ffstring[i]),ffstring[i],(i==(l-1)))
            self.screenDoReturnCarriage()
            self.screenDoNewLine()

    def screenFlush(self):
        """
        Make sure the screen is redrawn.
        """
        self.changed += 1
        self.doUpdate(27)

    def screenDoBell(self):
        """
        Make a bell-like noise. Or something like that.
        In order to make the NOS APL 2 editor work as expected, this always
        flushes all text to the screen.
        """
        make_noise(os.path.join(os.getcwd(),self.bell_wav))
        self.screenFlush()

    def screenAddChar(self,charnum,is_shift,is_ctrl,is_alt,is_printable,do_update):
        """
        Screen: Add character charnum to current line.
        In most applications (all?) the modifer key states will not be available,
        so this is almost always more complex than necessary.
        """
        self.screenAddCharSimple(charnum,is_printable,do_update)

    def screenAddCharSimple(self,charnum,is_printable,do_update):
        """
        Screen: Add character charnum to current line.
        """
        # If the character location is at the start of the line now, empty the line.
        if self.prevlen == 0:
            self.line = []
        # Conditionally add the character.
        if is_printable or self.shownonprint:
            self.screenlock.acquire()
            self.line.append(charnum)
            self.changed = 2
            self.prevlen += 1
            self.screenlock.release()
            if self.debuglevel > 2:
                print('--> prevlen',self.prevlen)
        # Conditionally update the display.
        if do_update:
            self.doUpdate(4)

    def screenAddString(self,string,newlinechar=10,retchar=13):
        """
        Screen: Add a string of characters to the screen.
        """ 
        # Step over the string characters. We need to know when we are at
        # the last because usually we only update the screen then. So count.
        string = _bytestostr_ifnot(string)
        l = len(string)
        for i in range(0,l):
            char = string[i]  # Current character as a character
            ichar = ord(char)  # Current character as a character code number
            # If there is an input mapping dictionary, apply it.
            # This only applies to single characters.
            if self.incharmap!= None:
                if ichar in self.incharmap:
                    ichar = self.incharmap[ichar]
            # We should usually treat LF as the signal to move to a new line.
            # Not CR. This is sort of obvious ... and sort of not.
            # And it is not really that simple. CR needs to reset the char position
            # to the start of the line. And LF must not do that.
            if ichar == newlinechar:
                if not self.suppress_next_newline_display:
                    self.screenDoNewLine()
                else:
                    self.suppress_next_newline_display = False
            elif ichar == retchar:
                self.screenDoReturnCarriage()
            elif ichar == 7:
                self.screenDoBell()
            elif ichar == 8:
                self.screenDoBackspace()
            elif ichar == 9:
                self.screenDoTab()
            elif ichar == 12:
                self.screenDoFormFeed()
            else:
                # If this is the escape character, set escape processing mode.
                if self.do_not_process_escapes:
                    self.inescape = False
                else:
                    self.checkEscapeStart(char)
                # If in escape processing mode, send the character to a user defined
                # processing function. This returns a "stay in escape" or not flag and
                # a string to insert in the screen (or None).
                if self.inescape:
                    if self.escapeProcessFunc != None:
                        (stayEscape,resultList,self.numescape,self.grafescape) = \
                            self.escapeProcessFunc(char,ichar,self.escapeseq,self.numescape)
                        self.inescape = stayEscape
                        if resultList != None:
                            if self.grafescape:
                                self.addGraphics(resultList)
                            else:
                                for c in resultList:
                                    self.screenAddCharSimple(c,True,True)
                        if not self.inescape:
                            self.escapeProcessFunc = None
                            self.numescape = 0
                # Otherwise add the character to the screen.
                else:
                    self.screenAddCharSimple(ichar,self.printableChar(char),(i==(l-1)))

    def screenAddCodesArray(self, array):
        """
        Screen: Write characters given as character codes to the current line 
        with no interpretation. Used for local history recall and editing.
        """
        l = len(array)
        for i in range(0,l):
            self.screenAddCharSimple(array[i],True,(i==(l-1)))

    def setEscapeProcessFunc(self,eschar,pfunc):
        """
        Set a function, pfunc, to process escape sequences which begin with eschar.
        """
        if self.escapeProcessFuncList != []:
            for fd in self.escapeProcessFuncList:
                (ec,epf) = fd
                if ec == eschar:
                    print('**** Escape character already has a processing function.')
                    return
        # Add this (eschar,pfunc) to the list of processing functions.
        self.escapeProcessFuncList.append((eschar,pfunc))

    def setSuppressNextNewlineDisplay(self,yes):
        """
        Throw away the next newline. Needed to get NOS 2 APL ^H^J "backspace"
        sequence to behave as a single backspace would in modern systems.
        """
        self.suppress_next_newline_display = yes

    def checkEscapeStart(self,testchar):
        """
        See if testchar is an escape sequence start character. If so, set its processing
        function as the current escape sequence processor, empty the accumulated esc seq,
        and mark us as being in esc seq processing mode.
        """
        if self.inescape or self.escapeProcessFuncList == []:
            if self.debuglevel > 2:
                print('*** checkEscapeStart({0}): inescape={1}, len(escapeProcessFuncList)={2}'.format(testchar,self.inescape,len(self.escapeProcessFuncList)))
            return
        for fd in self.escapeProcessFuncList:
            (ec,epf) = fd
            if ec == testchar:
                if self.debuglevel > 2:
                    print('*** checkEscapeStart({0}): setting new escape func for char:',testchar)
                self.inescape = True
                self.escapeseq = []
                self.escapeProcessFunc = epf
                self.numescape = 0
                self.grafescape = False

    def clearEscapeProcessors(self):
        """
        Empty the escape sequence processor function list.
        """
        self.escapeProcessFuncList = []

    def doUpdate(self,location):
        """
        Re-paint the screen. This is always called indirectly
        via a custom SIGNAL to try to have all OpenGL rendering done
        on the main thread even if characters are being added from a
        separate thread - which is necessary for most comms applications.
        """
        # If the screen data has actually changed, repaint. Otherwise, do nothing.
        # Many unnecessary repaint events may be queued, so this greatly improves performance.
        # However, there is a nasty kludge which seems to be required to make this work
        # reliably ... repaint one more time than seems to be strictly necessary!
        if self.changed > 0:
            self.update()
            self.screenlock.acquire()
            self.changed -= 1
            self.screenlock.release()
        if self.debuglevel > 1:
            print('Update. From:',location,' Changed:',self.changed)

    def keyboardGotReturn(self):
        """
        Keyboard return key handler.
        """
        self.screenDoNewLine()

    def keyboardGotBackspace(self):
        """
        Keyboard backspace key handler.
        """
        self.screenDoBackspace()

    def keyboardGotChar(self,charnum,is_shift,is_ctrl,is_alt,is_printable):
        """
        Keyboard normal character key handler.
        """
        self.screenAddChar(charnum,is_shift,is_ctrl,is_alt,is_printable,True)

    def keyPressEvent(self,event):
        """
        Handle the keyboard - key presses.
        """
        keynum = event.key()
        if self.debuglevel > 0:
            print('KeyPress',keynum,event.text())
        # Look for modifier keys first.
        if keynum == self.QtControlKeyCode:
            self.ctrl = True
        elif keynum == Qt.Key_Shift:
            self.shift = True
        elif keynum == Qt.Key_Alt or keynum == Qt.Key_AltGr:
            self.alt = True
        elif keynum == Qt.Key_CapsLock:
            self.shiftlock = not self.shiftlock
        else:
            # Backspace and Return keys.
            if keynum > 131:
                if keynum == Qt.Key_Backspace:
                    self.keyboardGotBackspace()
                elif keynum == Qt.Key_Return:
                    self.keyboardGotReturn()
                else:
                    if keynum in self.fancykeymap:
                        fancykeystring = self.fancykeymap[keynum]
                        for c in fancykeystring:
                            self.keyboardGotChar(ord(c),False,False,False,True)
                    else:
                        self.specialUnfancyKey(keynum)
            # Other keys.
            else: 
                # Convert keynum to ASCII
                shifted = self.shift or self.shiftlock
                # Lower case alpha.
                if keynum > 64 and keynum < 91 and not shifted:
                    self.icharnum = keynum + 32
                else:
                    self.icharnum = keynum
                # Special case for # key on Mac keyboards.
                patched_macos_hash = False
                if self.iam_macos and self.icharnum == 51 and self.alt:
                    self.icharnum = 35
                    patched_macos_hash = True
                # See if printable.
                printable = not( self.ctrl or (self.alt and not patched_macos_hash) )
                # Mask off if ctrl modifier down.
                if self.ctrl:
                    self.icharnum = self.icharnum & 31
                self.keyboardGotChar(self.icharnum,self.shift,self.ctrl,self.alt,printable)

    def specialUnfancyKey(self, charnum):
        """
        A special key not handled by fancykeymap. Do nothing here, but can override.
        Used now for local history recall and editing.
        """
        pass

    def keyReleaseEvent(self,event):
        """
        Handle the keyboard - key releases.
        """
        keynum = event.key()
        if self.debuglevel > 1:
            print('KeyRelease',keynum,event.text())
        # Turn off modifiers on modifier key release.
        if keynum == self.QtControlKeyCode:
            self.ctrl = False
        elif keynum == Qt.Key_Shift:
            self.shift = False
        elif keynum == Qt.Key_Alt or keynum == Qt.Key_AltGr:
            self.alt = False

    def clearScreen(self):
        """
        Clear the screen.
        """
        if self.drawgraf:
            self.gcblock.acquire()
            self.gcbcmds = 0
            self.gcb = []
            self.gchanged = 2
            self.gcblock.release()
            self.doGrUpdate(2)
        else:
            self.screenlock.acquire()
            self.line = []
            self.screen = []
            self.changed = 2
            self.screenlock.release()
            self.doUpdate(5)

    def printableChar(self,char):
        """
        Return True if char is printable. This may need to be adjusted for some uses.
        """
        return( char in string.printable and char != '\r' )

    def focusInEvent(self,event):
        """
        Handle gain of focus.
        """
        if self.debuglevel > 1:
            print('@@@ got focus')
        self.havefocus = True
        self.screenlock.acquire()
        self.changed = 2
        self.screenlock.release()
        self.doUpdate(6)


    def focusOutEvent(self,event):
        """
        Handle loss of focus.
        """
        if self.debuglevel > 1:
            print('@@@ lost focus')
        self.havefocus = False
        self.screenlock.acquire()
        self.changed = 2
        self.screenlock.release()
        self.doUpdate(7)

    def backspaceSendsDelete(self,yes):
        """
        Make backspace key send delete code. Or not.
        """
        if yes:
            self.outcharmap[8] = 127
            self.outcharmap[127] = 127
            self.incharmap[8] = 8
            self.incharmap[127] = 8
        else:
            self.outcharmap[8] = 8
            self.outcharmap[127] = 127
            self.incharmap[8] = 8
            self.incharmap[127] = 127

    def followBackspaceWithNewline(self,yes):
        """
        Send newline after every backspace (for NOS APL 2).
        """
        self.newline_after_backspace = yes

    def vkb_screen_pos_to_key(self,x,y):
        """
        Convert a screen mouse position to a virtual keyboard key number.
        """
        if self.vkb_have:
            xbase = self.viewport[0] - self.vkb_img.size[0]
            xkey = int((x-xbase)/self.vkb_keyxdelta)
            if xkey < 0 or xkey >= self.vkb_keycols:
                return -1
            ykey = int(y/self.vkb_keyydelta)
            if ykey < 0 or ykey >= self.vkb_keyrows:
                return -1
            return xkey + ykey * self.vkb_keycols
        else:
            return -1

    def vkb_key_to_screen_pos(self,keynum):
        """
        Convert a key number to a screen position (centered on the key).
        """
        if self.vkb_have:
            xbase = self.viewport[0] - self.vkb_img.size[0]
            maxkeynum = self.vkb_keyrows*self.vkb_keycols-1
            if keynum < 0 or keynum > maxkeynum:
                return(-1,-1)
            xkey = keynum % self.vkb_keycols
            xpos = self.vkb_keyxdelta * xkey + (self.vkb_keyxdelta*0.5)
            ykey = keynum // self.vkb_keycols
            ypos = self.vkb_keyydelta * ykey + (self.vkb_keyydelta*0.5)
            return(xpos+xbase,ypos)
        else:
            return(-1,-1)

    def mousePressEvent(self,mouseEvent):
        """
        Mouse button press handler.
        """
        if self.debuglevel > 0:
            print('Mouse press. Pos=({0},{1})'.format(mouseEvent.x(),mouseEvent.y()))
        # Virtual keyboard events?
        if self.vkb_have and self.vkb_show and not self.drawgraf:
            self.vkb_down_keynum = self.vkb_screen_pos_to_key(mouseEvent.x(),mouseEvent.y())
            if self.debuglevel > 0:
                if self.vkb_down_keynum < 0:
                    print("Off keyboard")
                else:
                    print(self.vkb_keymap[self.vkb_down_keynum])
            self.vkb_tooltip = ( mouseEvent.buttons() == Qt.RightButton )
            self.update()
            if not self.vkb_tooltip:
                if self.vkb_down_keynum >= 0:
                    self.keyboardGotChar(self.vkb_keymap[self.vkb_down_keynum][0],False,False,False,True)

    def mouseReleaseEvent(self,mouseEvent):
        """
        Mouse button release handler.
        """
        if self.debuglevel > 0:
            print('Mouse release. Pos=({0},{1})'.format(mouseEvent.x(),mouseEvent.y()))
        self.vkb_down_keynum = -1
        self.update()

    def mouseDoubleClickEvent(self,mouseEvent):
        """
        Mouse button double-click handler.
        """
        if self.debuglevel > 0:
            print('Mouse double click.')

    def mouseMoveEvent(self,mouseEvent):
        """
        Mouse movement handler.
        """
        mousebuttons = int(mouseEvent.buttons())
        if mousebuttons != Qt.NoButton:
            delta_x = mouseEvent.x() - self.oldmouse_x
            delta_y = self.oldmouse_y - mouseEvent.y()
            if self.debuglevel > 0:
                print('Mouse drag. Delta=({0},{1})'.format(delta_x,delta_y))
        self.oldmouse_x = mouseEvent.x()
        self.oldmouse_y = mouseEvent.y()

    def wheelEvent(self,wheelEvent):
        """
        Mouse wheel movement handler.
        Use this to change the scroll position.
        """
        change = wheelEvent.angleDelta().y()
        if change < 0:
            self.scroll += 1
        else:
            self.scroll -= 1
        self.setScroll(self.scroll)

    def openLogFile(self,logfilename):
        """
        Open a log file to which unicode characters can be written.
        """
        try:
            self.flog = codecs.open(logfilename,mode='w',encoding='utf-8')
        except:
            self.flog = None

    def writeLogFile(self,ourcharcodestring):
        """
        Write a line to the Unicode log file.
        """
        try:
            for ccode in ourcharcodestring:
                ccodeunic = self.unicode_map[ccode]
                self.flog.write(ccodeunic)
            self.flog.write('\n')
            self.flog.flush()
        except:
            print('writeLogFile() failed. Python 3 Unicode problem.')

    def closeLogFile(self):
        """
        Close the logfile.
        """
        self.flog.close()
        self.flog = None

    def lint(self,charlist):
        """
        Graphics: Convert a list containing an ascii character in each element to an integer.
        """
        hs = ''
        for e in charlist:
            hs += chr(e)
        return int(hs)

    def lfcol(self,charlist):
        """
        Graphics: Convert a colour integer char list to a floating point normalized colour.
        """
        ival = self.lint(charlist)
        return float(ival)/999.0

    def lfwid(self,charlist):
        """
        Graphics: Convert a width integer char list  to a floating point width.
        """
        ival = self.lint(charlist)
        return float(ival)/99.0

    def lfpos(self,charlist):
        """
        Graphics: Convert a coordinate component char list to a normalized floating point position.
        """
        ival = self.lint(charlist)
        return float(ival)/9999.0

    def alt_float(self,floatstring):
        """
        Graphics: Convert a floating point number string to float for alt_escmode (Cyber APL).
        This has negative numbers that begin $NG...
        """
        if floatstring[0] == '$':
            return -float(floatstring[3:])
        else:
            return float(floatstring)

    def addGraphics(self,commandlist):
        """
        Graphics: Add a command to the graphics command buffer.
        This can parse two quite different representations of the same information, depending
        on if the escape character is <ESCAPE> or if it is @. The latter case indicates that data
        will be passed a space separated list elements rather than fixed width integers (it is needed
        for drawing from APL).
        """
        if self.debuglevel > 2:
            print("GRAPHICS:",commandlist)

        # Acquire display list lock.
        self.gcblock.acquire()
        isaflush = False
        
        # Trap errors to prevent aborts with experimental drivers.
        command = -1
        try:
            # Get the command as a character code.
            command = commandlist[2]
            # See if <escape> or @ is the escape charatcter. If @ make a string version
            # of the character code lists and split it at white space to a list of strings.
            alt_escmode = False
            if commandlist[0] == 64:
                alt_escmode = True
                commandstring = ''
                for commandlistelement in commandlist:
                    commandstring += chr(commandlistelement)
                commandsplit = commandstring.split()
                self.setSuppressNextNewlineDisplay(True)
                
            # Decode command, get arguments, add command tuple to command list.
            if command == 48:
                # 0: clear gcb list.
                self.gcbcmds = 0
                self.gcb = []
                isaflush = True
                if self.debuglevel > 2:
                    print("CLEAR")
                    
            elif command == 49:
                # 1: set colour.
                if alt_escmode:
                    cred = float(commandsplit[1])
                    cgrn = float(commandsplit[2])
                    cblu = float(commandsplit[3])
                else:
                    cred = self.lfcol(commandlist[3:6])
                    cgrn = self.lfcol(commandlist[6:9])
                    cblu = self.lfcol(commandlist[9:12])
                self.gcb.append((1,cred,cgrn,cblu))
                if self.debuglevel > 2:
                    print("COLOUR", self.gcb[-1])
                    
            elif command == 50:
                # 2: fill/erase.
                self.gcb.append((2,0))
                if self.debuglevel > 2:
                    print("FILL")
                    
            elif command == 51:
                # 3: move.
                if alt_escmode:
                    x = self.alt_float(commandsplit[1])
                    y = self.alt_float(commandsplit[2])
                else:
                    x = self.lfpos(commandlist[3:7])
                    y = self.lfpos(commandlist[7:11])
                self.gcb.append((3,x,y))
                if self.debuglevel > 2:
                    print("MOVE", self.gcb[-1])
                    
            elif command == 52:
                # 4: draw.
                if alt_escmode:
                    x = self.alt_float(commandsplit[1])
                    y = self.alt_float(commandsplit[2])
                else:
                    x = self.lfpos(commandlist[3:7])
                    y = self.lfpos(commandlist[7:11])
                self.gcb.append((4,x,y))
                if self.debuglevel > 2:
                    print("DRAW", self.gcb[-1])
                    
            elif command == 53:
                # 5: flush
                isaflush = True
                if self.debuglevel > 2:
                    print("FLUSH")
                    
            elif command == 54:
                # 6: width
                if alt_escmode:
                    width = float(commandsplit[1])
                else:
                    width = self.lfwid(commandlist[3:6])
                self.gcb.append((6,width))
                if self.debuglevel > 2:
                    print("WIDTH", self.gcb[-1])
                    
            elif command == 55:
                # 7: bounds. ONLY in alt_escmode.
                if alt_escmode:
                    xlo = self.alt_float(commandsplit[1])
                    ylo = self.alt_float(commandsplit[2])
                    xhi = self.alt_float(commandsplit[3])
                    yhi = self.alt_float(commandsplit[4])
                    self.gcb.append((7,xlo,ylo,xhi,yhi))
                    if self.debuglevel > 2:
                        print("BOUNDS", self.gcb[-1])

            elif command == 56:
                # 8: graph bounds. ONLY in alt_escmode.
                if alt_escmode:
                    xlo = self.alt_float(commandsplit[1])
                    ylo = self.alt_float(commandsplit[2])
                    xhi = self.alt_float(commandsplit[3])
                    yhi = self.alt_float(commandsplit[4])
                    self.gcb.append((8,xlo,ylo,xhi,yhi))
                    if self.debuglevel > 2:
                        print("GRAPH BOUNDS", self.gcb[-1])

            elif (command == 57) or (command == 69):
                # 9: graphics text string. ONLY in alt_escmode.
                # E: graph title.
                #print 'addGraphics(): graphics text'
                #print ' ... commandlist =',commandlist
                if alt_escmode:
                    recovered_string = ''
                    for i in range(4,len(commandlist)-1):
                        recovered_string += chr(commandlist[i])
                    #print ' ... recovered string:'recovered_string
                    icmd = 9 if (command == 57) else 14
                    self.gcb.append((icmd,recovered_string))
                    if self.debuglevel > 2:
                        if command == 57:
                            print("TEXT", self.gcb[-1])
                        else:
                            print("TITLE", self.gcb[-1])
                            
            elif command == 65:
                # A: font size. ONLY in alt_escmode.
                fs = self.alt_float(commandsplit[1])
                self.gcb.append((10,fs))
                if self.debuglevel > 2:
                    print("FONT SIZE", self.gcb[-1])                

            elif command == 66:
                # B: text align. ONLY in alt_escmode.
                fs = self.alt_float(commandsplit[1])
                self.gcb.append((11,fs))
                if self.debuglevel > 2:
                    print("TEXT ALIGN", self.gcb[-1])                

            elif command == 67:
                # C: font index. ONLY in alt_escmode.
                fs = self.alt_float(commandsplit[1])
                self.gcb.append((12,fs))
                if self.debuglevel > 2:
                    print("FONT INDEX", self.gcb[-1])                

            elif command == 68:
                # D: draw point marker. ONLY in alt_escmode.
                x = self.alt_float(commandsplit[1])
                y = self.alt_float(commandsplit[2])
                self.gcb.append((13,x,y))
                if self.debuglevel > 2:
                    print("POINT", self.gcb[-1])

            elif command == 70:
                # F: draw circle. ONLY in alt_escmode.
                x = self.alt_float(commandsplit[1])
                y = self.alt_float(commandsplit[2])
                r = self.alt_float(commandsplit[3])
                self.gcb.append((15,x,y,r))
                if self.debuglevel > 2:
                    print("CIRCLE", self.gcb[-1])

            elif command == 71:
                # G: set/clear square mode. ONLY in alt_escmode.
                is_square = self.alt_float(commandsplit[1])
                self.gcb.append((16,is_square))
                if self.debuglevel > 2:
                    print("SET_SQUARE", self.gcb[-1])

            # If command wasn't clear display list, bump display list command count.
            if command != 48:
                self.gcbcmds += 1;

            # Release the display list lock.
            self.gcblock.release()
            
            # If we have received a lot of commands, or a flush command, update the screen.
            if isaflush or ( ( ( (self.gcbcmds+1) % 1000 ) ) == 0 ):
                self.gchanged = 2
                self.doGrUpdate(1)

        # If there was an exception, try to say what happened.
        except Exception as e:
            print('add_graphics(): Exception, command code:',command)
            print(e)
            self.gcblock.release()

    def viewGraphics(self):
        """
        View the graphics screen.
        """
        self.drawgraf = True
        self.update()

    def viewText(self):
        """
        View the text screen.
        """
        self.drawgraf = False
        self.update()

    def doGrUpdate(self,location):
        """
        Re-paint the graphics screen. This is always called indirectly
        via a custom SIGNAL to try to have all OpenGL rendering done
        on the main thread even if characters are being added from a
        separate thread - which is necessary for most comms applications.
        """
        # If the graphics screen data has actually changed, repaint. Otherwise, do nothing.
        # Logic identical to doUpdate.
        if self.gchanged > 0:
            self.update()
            self.gcblock.acquire()
            self.gchanged -= 1
            self.gcblock.release()
        if self.debuglevel > 1:
            print('GrUpdate. From:',location,' Changed:',self.gchanged)

    def cairoSetLineWidth(self, c, w):
        """
        Set the line width in Cairo. The line width must be specified in "user units" ...
        It seems impossible to get Cairo line widths to exactly match OpenGL line widths.
        Not exactly sure why, but there are plenty of possibilities.
        """
        uw,uh = c.device_to_user_distance(w,w)
        dw = min(uw,uh)
        if self.debuglevel > 2:
            print('cairoSetLineWidth(), w =',w,' dw =',dw)
        c.set_line_width(dw)

    def cairoRenderGraphics(self,c,to_x_pixels,to_y_pixels):
        """
        Render the graphics command buffer contents to Cairo context c.
        """
        # Available font names. These WILL be OS specific.
        fontnames = ['Times New Roman','Arial','Courier']
        
        # Acquire the display list lock.
        self.gcblock.acquire()
        inaline = False
        
        # Record MOVE commands, but do not actually move until the first
        # DRAW after a MOVE.
        pending_move = False
        pmx = 0.0
        pmy = 0.0

        # Set the initial state variables.
        x_scale = to_x_pixels
        y_scale = to_y_pixels
        x_offset = 0.0
        y_offset = 0.0
        width = 1.0
        gcolour = [1.0, 1.0, 1.0]
        fontsize = 14
        fontindex = 0
        textalign = 0
        make_square = False

        # Set font attributes in case text is drawn.
        c.select_font_face( fontnames[fontindex], cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL )
        c.set_font_size( fontsize )
        
        # Always start by clearing to black. and setting white as the drawing colour.
        c.set_source_rgb(0.0, 0.0, 0.0)
        c.paint()

        # Set the initial state variables into Cairo.
        self.cairoSetLineWidth(c,width)
        c.set_source_rgb(gcolour[0], gcolour[1], gcolour[2])
        
        # Draw all the commands in the graphics command buffer.
        for cmd in self.gcb:
            if self.debuglevel > 2:
                print('cairoRenderGraphics(): cmd =',cmd)
                
            # If cmd is not draw, if in a line, end the line.
            if cmd[0] != 4:
                if inaline:
                    c.stroke()
                    inaline = False
                    
            # Execute each command
            if cmd[0] == 1: # Set colour
                gcolour = cmd[1:]
                c.set_source_rgb(gcolour[0], gcolour[1], gcolour[2])
                
            elif cmd[0] == 2: # Fill/erase
                c.paint()
                
            elif cmd[0] == 3: # Move. Should be followed by one or more draws.
                gpos = cmd[1:]
                pending_move = True
                pmx = (gpos[0] - x_offset) * x_scale
                pmy = (gpos[1] - y_offset) * y_scale
                
            elif cmd[0] == 4: # Draw. Add line segment to line.
                if pending_move:
                    c.move_to(pmx,to_y_pixels-pmy)
                    pending_move = False
                    inaline = True
                if inaline:
                    gpos = cmd[1:]
                    x = (gpos[0] - x_offset) * x_scale
                    y = (gpos[1] - y_offset) * y_scale
                    c.line_to(x,to_y_pixels-y)
                    
            elif cmd[0] == 6: # Width.
                width = cmd[1]
                self.cairoSetLineWidth(c,width)
                
            elif cmd[0] == 7: # Bounds. xlo, ylo, xhi, yhi
                if make_square:
                    y_offset = cmd[2]
                    y_scale = to_y_pixels / max(1e-6, cmd[4] - cmd[2])
                    x_offset = cmd[1]
                    x_scale = y_scale
                    pass
                else:
                    x_offset = cmd[1]
                    x_scale = to_x_pixels / max(1e-6, cmd[3] - cmd[1])
                    y_offset = cmd[2]
                    y_scale = to_y_pixels / max(1e-6, cmd[4] - cmd[2])

            elif cmd[0] == 8: # Graph bounds. xlo, ylo, xhi, yhi
                # Find tick values for each axis.
                if make_square:
                    xmid = 0.5 * ( cmd[1] + cmd[3] )
                    xdelta = 0.5 * ((float(to_x_pixels) / float(to_y_pixels)) * (cmd[4] - cmd[2]))
                    graph_tick_values_x = grid.tick_values( xmid-xdelta, xmid+xdelta, 15 )
                else:
                    graph_tick_values_x = grid.tick_values( cmd[1], cmd[3], 15 )
                graph_tick_values_y = grid.tick_values( cmd[2], cmd[4], 10 )
                # Set the drawing bounds to the smallest and largest tick values on each axis.
                xlo = graph_tick_values_x[0]
                xhi = graph_tick_values_x[-1]
                ylo = graph_tick_values_y[0]
                yhi = graph_tick_values_y[-1]
                if make_square:
                    y_offset = ylo
                    y_scale = to_y_pixels / max(1e-6, yhi - ylo)
                    x_offset = xlo
                    x_scale = y_scale
                else:
                    x_offset = xlo
                    x_scale = to_x_pixels / max(1e-6, xhi - xlo)
                    y_offset = ylo
                    y_scale = to_y_pixels / max(1e-6, yhi - ylo)
                # Now draw the graph paper ...
                # First, make label strings for the tick values (already set).
                x_labels,x_scale_string = grid.tick_labels( graph_tick_values_x )
                n_x_labels = len(x_labels)
                y_labels,y_scale_string = grid.tick_labels( graph_tick_values_y )
                n_y_labels = len(y_labels)
                # Set drawing state for the graph paper.
                c.set_font_size(14)
                self.cairoSetLineWidth(c,0.5)
                c.set_source_rgb(0.0,0.0,0.0)
                # Draw the vertical lines for the horizontal axis.
                for xc in graph_tick_values_x:
                    c.move_to((xc-x_offset)*x_scale,to_y_pixels-(ylo-y_offset)*y_scale)
                    c.line_to((xc-x_offset)*x_scale,to_y_pixels-(yhi-y_offset)*y_scale)
                    c.stroke()
                # Draw horizontal lines for the vertical axis.
                for yc in graph_tick_values_y:
                    c.move_to((xlo-x_offset)*x_scale,to_y_pixels-(yc-y_offset)*y_scale)
                    c.line_to((xhi-x_offset)*x_scale,to_y_pixels-(yc-y_offset)*y_scale)
                    c.stroke()
                # Horizontal axis labels.
                yc = (graph_tick_values_y[1] - y_offset) * y_scale
                for i in range(0,n_x_labels):
                    xc = (graph_tick_values_x[i] - x_offset) * x_scale
                    c.move_to(xc+0.5*self.charspace,to_y_pixels-(yc-0.7*self.linespace))
                    c.show_text(x_labels[i])
                if len(x_scale_string) > 0:
                    xc = (graph_tick_values_x[-2] - x_offset) * x_scale
                    yc = (graph_tick_values_y[1] - y_offset ) * y_scale
                    c.move_to(xc+0.5*self.charspace,to_y_pixels-(yc-2.2*self.linespace))
                    c.show_text(x_scale_string)
                # Vertical axis labels.
                xc = (graph_tick_values_x[1] - x_offset) * x_scale
                for i in range(0,n_y_labels):
                    yc = (graph_tick_values_y[i] - y_offset) * y_scale
                    c.move_to(xc+0.5*self.charspace,to_y_pixels-(yc+0.2*self.linespace))
                    c.show_text(y_labels[i])
                if len(y_scale_string) > 0:
                    yc = (graph_tick_values_y[-2] - y_offset) * y_scale
                    xc = (graph_tick_values_x[1] - x_offset ) * x_scale
                    c.move_to(xc+0.5*self.charspace,to_y_pixels-(yc+1.7*self.linespace))
                    c.show_text(y_scale_string)
                # Restore previous drawing state.
                c.set_source_rgb(gcolour[0], gcolour[1], gcolour[2])
                self.cairoSetLineWidth(c,width)
                c.set_font_size(fontsize)

            elif cmd[0] == 9: # Graphics text: draw string at last move_to position.
                if textalign == 0: # Start at pos.
                    c.move_to(pmx,to_y_pixels-pmy)
                else:
                    txb, tyb, tw, th, tdx, tdy = c.text_extents(cmd[1])
                    if textalign == 1: # Horizontal center on pos.
                        c.move_to(pmx-tw//2,to_y_pixels-pmy)
                    elif textalign == 2: # End at pos.
                        c.move_to(pmx-tw,to_y_pixels-pmy)
                    elif textalign == 3: # Center horizontally in the display.
                        c.move_to((to_x_pixels-tw)//2,to_y_pixels-pmy)
                c.show_text(cmd[1])

            elif cmd[0] == 10: # Font size.
                fontsize = int( cmd[1] )
                c.set_font_size(fontsize)

            elif cmd[0] == 11: # Text alignment.
                textalign = int( cmd[1] )

            elif cmd[0] == 12: # Font index.
                fontindex = max(0, min( len(fontnames)-1, int( cmd[1] ) ) )
                c.select_font_face( fontnames[fontindex], cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL )

            elif cmd[0] == 13: # Draw a point marker.
                delta = int( 0.005 * to_x_pixels ) + 1
                gpos = cmd[1:]
                pmx = (gpos[0] - x_offset) * x_scale
                pmy = (gpos[1] - y_offset) * y_scale
                c.move_to( pmx-delta, to_y_pixels-pmy )
                c.line_to( pmx+delta, to_y_pixels-pmy )
                c.move_to( pmx, to_y_pixels-pmy-delta )
                c.line_to( pmx, to_y_pixels-pmy+delta )
                c.stroke()

            elif cmd[0] == 14: # Draw a graph title.
                c.select_font_face( fontnames[1], cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL )
                c.set_font_size( 40 )
                txb, tyb, tw, th, tdx, tdy = c.text_extents(cmd[1])
                c.move_to( (to_x_pixels-tw)//2,2.5*th)
                c.show_text(cmd[1])
                c.select_font_face( fontnames[fontindex], cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL )
                c.set_font_size(fontsize)

            elif cmd[0] == 15: # Draw a circle.
                pmx = (cmd[1] - x_offset) * x_scale
                pmy = (cmd[2] - y_offset) * y_scale
                prd = cmd[3] * x_scale
                c.arc( pmx, pmy, prd, 0, 2*math.pi )
                c.stroke()

            elif cmd[0] == 16: # Set/clear square mode.
                make_square = ( cmd[1] > 0.0 )

        # If in a line after the last command, end the line.
        if inaline:
            c.stroke()

        # Release the display list lock.
        self.gcblock.release()

    def saveGraphics(self,filename):
        """
        Save the graphics data to an SVG file using Cairo.
        """
        if self.gcbcmds > 0:
            (root,ext) = os.path.splitext(filename)
            outfilename = root + '.svg'
            s = cairo.SVGSurface(outfilename,self.width_pixels,self.height_pixels)
            c = cairo.Context(s)
            self.cairoRenderGraphics(c,self.width_pixels,self.height_pixels)
            s.finish()

    def cairoRenderGraphicsToTexture(self,imwidth,imheight):
        """
        Use Cairo to generate a higher quality screen image than OpenGL can manage.
        This renders to a texture then a rectangle with that texture is drawn to cover
        the graphics viewport (in paintGL()).
        """
        if self.gcbcmds > 0:
            s = cairo.ImageSurface(cairo.FORMAT_ARGB32, imwidth, imheight )
            c = cairo.Context(s)
            self.cairoRenderGraphics(c,imwidth,imheight)
            self.crgraf_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D,self.crgraf_texture)
            s_data = s.get_data()
            glPixelStorei(GL_UNPACK_ALIGNMENT,1)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP )
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP )
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST )
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, imwidth, imheight, 0, GL_BGRA, \
                             GL_UNSIGNED_INT_8_8_8_8_REV, s_data)

    def setScroll(self,scrollvalue):
        """
        Set the text scroll value.
        """
        self.scroll = min( self.maxlines, max( 0, scrollvalue ) )
        self.update()

    def deltaScroll(self,deltascrollvalue):
        """
        Add deltascrollvalue to the text scroll value.
        """
        self.scroll = min( self.maxlines, max( 0, self.scroll + deltascrollvalue ) )
        self.update()        

    def setFFMode(self,clears):
        """
        Set how to handle form feeds.
        """
        self.ffclears = clears

    def setOnPaper(self,paper):
        """
        Use a green bar paper background. Or not.
        """
        self.papermode = paper
        self.update()

    def set_horizontal_guide(self, guide_pos):
        """
        Set an array of horizontal positions at which to draw guide lines.
        """
        self.h_guide_positions = guide_pos

    def clearModifiers(self):
        """
        Turn all modifier keys off.
        """
        self.ctrl = False
        self.shift = False
        self.shiftlock = False
        self.alt = False


###########################
# GTermTelnetWidget CLASS #
###########################

class GTermTelnetWidget(GTermWidget):
    """
    Implement a glass teletype connected to a remote host via telnet.
    """
    def __init__(self, charsetname='unknown',vkbname='unknown',umapname='unknown',parent=None):
        super(GTermTelnetWidget, self).__init__(charsetname,vkbname,umapname,parent)
        self.telnet = None
        self.scr_thread = None
        self.localecho = False
        self.haveconnection = False
        self.char_to_string_map = None
        self.terminate_char = 3 # Ctrl-C default interrupt character.
        self.history_line = []
        self.history_buffer = []
        self.history_max = 512
        self.history_level = -1
        self.local_recall = False
        self.edit_offset = 0
        self.editing = False
        self.prev_editing = False

    def open_conn(self,host,port,debuglevel=0):
        """
        Open a connection to a remote host.
        Host is a string, port is an integer.
        """
        try:
            self.telnet = XTelnet(host,port)
            self.telnet.set_data_received_function(self.data_received)
            self.telnet.set_eof_func(self.telnet_eof_func)
            if debuglevel > 0:
                self.telnet.set_debuglevel(debuglevel)
            #self.telnet.set_debuglevel(10)
            # Reading data from the remote host needs to be done on a separate thread.
            self.scr_thread = threading.Thread(target=readserver_thread, args=(self.telnet,0))
            self.scr_thread.start()
            self.haveconnection = True
            self.connect_time = time.strftime("%a %d %b %Y %X", time.localtime())
        except:
            self.telnet = None
            self.haveconnection = False
            self.connect_time = 'Zero'
            errstring = 'Cannot connect to: {0} at port: {1}.'.format(host,port)
            self.screenAddString(errstring)

    def telnet_eof_func(self):
        """
        Function called when the Telnet connection closes.
        """
        self.screenAddString('\r\nTelnet connection closed by remote host.')
        self.haveconnection = False

    def data_received(self,recvstr):
        """
        Handle a string received from the remote host.
        """
        # NOTE WELL: This will be running in its own thread usually!
        if self.debuglevel > 0:
            print('>>>>',recvstr)
        if self.debuglevel > 2:
            dumpData(recvstr)
        self.screenAddString(recvstr)

    def set_local_echo(self,yes):
        """
        Turn local echoing on or off.
        """
        self.localecho = yes

    def set_local_recall(self,yes):
        """
        Set local command recall (or remote host recall).
        """
        self.local_recall = yes

    def set_terminate_char(self,charint):
        """
        Set the character that will terminate a program.
        This isn't actually currently used for anything!
        """
        self.terminate_char = charint

    def set_escape_on_off(self,noesc):
        """
        Turn escape processing on or off.
        """
        self.do_not_process_escapes = noesc

    def telnet_write(self,charstring):
        bytestring = charstring.encode('ASCII')
        self.telnet.write(bytestring)

    def send_char(self,char):
        """
        Send a character to the remote host.
        """
        # Do nothing if there is no connection.
        if self.haveconnection:
            # Local echo handling
            if self.localecho:
                if char == 13:
                    self.screenDoNewLine()
                elif char == 8:
                    self.screenDoBackspace()
                else:
                    self.screenAddCharSimple(char,True,True)
            # If there is an output mapping dictionary, apply it.
            # This allows for single character substitutions only.
            if self.outcharmap != None:
                if char in self.outcharmap:
                    char = self.outcharmap[char]
            # Make sure <return> (key) actually sends <CR><LF> as Telnet defines it should.
            if self.telnet != None:
                if char == '\r':
                    self.telnet_write('\r\n')
                else:
                    self.telnet_write(chr(char))

    def to_chars(self, array ):
        """
        Debug aid: Convert an array of character codes to a string.
        """
        result = ''
        for ival in array:
            result += chr(ival)
        return result
    
    def addLineToHistory(self):
        """
        Add a line to the local history buffer.
        """
        if self.local_recall:
            self.history_buffer.append(self.history_line)
            if len(self.history_buffer) > self.history_max:
                self.history_buffer.pop(0)
            self.history_line = []
            if self.debuglevel > 2:
                for ihist in range(len(self.history_buffer)-1,-1,-1):
                    print(ihist, self.history_buffer[ihist], self.to_chars(self.history_buffer[ihist]))

    def keyboardGotReturn(self):
        """
        Keyboard return key handler.
        """
        # If we are doing local history recall and editing a line,
        # add the edited line to the history buffer. Stop editing.
        if self.editing and self.local_recall:
            self.addLineToHistory()
            # Make the newly added line the selected history line.
            self.history_level = 0
            self.editing = False
            self.prev_editing = False
        # If we are doing local history recall, and have a selected
        # history line, send the selected history line.
        if (self.history_level > -1) and self.local_recall:
            self.edit_offset = 0
            self.set_cursor_char_offset(self.edit_offset)
            self.screenClearLine()
            for c in self.history_buffer[len(self.history_buffer)-self.history_level-1]:
                self.sendCharacterStringMapped(c)
            self.send_char(13)
            self.history_level = -1
        # No selected history line. Send the current (newly entered) line.
        # If doing local recall processing, add that line to the history buffer.
        else:
            # Send the end-of-line to the host.
            # NOTE: The return key should send CR, which send_char() will send as CR LF
            # This is the correct indicator for "new line" going out.
            # For incoming data, LF should be treated as "new line" usually.
            self.send_char(13)
            if self.local_recall:
                self.addLineToHistory()

    def keyboardGotBackspace(self):
        """
        Keyboard backspace key handler.
        """
        send_to_host = True
        # Local history recall processing.
        if self.local_recall:
            if self.history_level == -1:
                # Entering a new line. Backspace removes last character from new history line too.
                if( len(self.history_line) > 0 ):
                    self.history_line.pop()
            else:
                # Editing a history line. Deal with this is keyboardGetChar().
                send_to_host = False
                self.keyboardGotChar(8,False,False,False,False)
        # In any case, send backspace to host unless editing a history line.
        if send_to_host:
            self.send_char(8) # May be further translated in send_char().
            if self.newline_after_backspace:
                self.send_char(10)
                self.setSuppressNextNewlineDisplay(True)

    def keyboardGotChar(self,charnum,is_shift,is_ctrl,is_alt,is_printable):
        """
        Keyboard normal character key handler.
        """
        self.editing = False
        # Local history recall processing.
        if self.local_recall:
            # Entering a new line.
            if self.history_level == -1:
                # Add character to the new history line.
                self.history_line.append(charnum)
            # Editing a history line. Get the selected history line array index and cursor position.
            else:
                self.editing = True
                hlineno = len(self.history_buffer) - self.history_level - 1
                # If not previously editing, make a copy of the selected history line.
                if not self.prev_editing:
                    self.history_line = list(self.history_buffer[hlineno])
                    self.prev_editing = True
                # Get the current length of the copy of the history line being edited
                # and get the character position from that and the edit_offset.
                ls = len(self.history_line)
                hcharno = ls - self.edit_offset
                # Editing command character processing.
                if charnum == 4:
                    # ^D: delete at cursor
                    if (hcharno >= 0) and (hcharno < ls):
                        del self.history_line[hcharno]
                        ls -= 1
                        self.edit_offset -= 1
                        self.edit_offset = max( 0, min( ls, self.edit_offset ) )
                        self.set_cursor_char_offset(self.edit_offset)
                elif charnum == 8:
                    # <backspace>: delete before cursor.
                    if (hcharno > 0) and (hcharno <= ls):
                        hcharno -= 1
                        del self.history_line[hcharno]
                        ls -= 1
                        self.edit_offset = max( 0, min( ls, self.edit_offset ) )
                        self.set_cursor_char_offset(self.edit_offset)
                elif charnum == 1:
                    # ^A: move to start of line.
                    self.edit_offset = ls
                    self.set_cursor_char_offset(self.edit_offset)
                elif charnum == 5:
                    # ^E: move to end of line.
                    self.edit_offset = 0
                    self.set_cursor_char_offset(self.edit_offset)
                else:
                    # Default: insert character at cursor position.
                    self.history_line.insert( hcharno, charnum )
                # Display the altered history line.
                self.screenClearLine()
                self.screenAddCodesArray(self.history_line)
        # In any case, if not editing a history line, send the character with char to string mapping.
        if not self.editing:
            self.sendCharacterStringMapped(charnum)

    def sendCharacterStringMapped(self,charnum):
        """
        Send a character but: If we have a mapping from a character to a string, 
        output the string in place of the character.
        """
        if self.char_to_string_map != None:
            # If we have a mapping from a character to a string, output the string
            # in place of the character.
            if charnum in self.char_to_string_map:
                outstring = self.char_to_string_map[charnum]
                if self.debuglevel > 1:
                    print(outstring)
                for c in outstring:
                    if self.debuglevel > 1:
                        print(c)
                    self.send_char(ord(c))
            else:
                self.send_char(charnum)
        else:
            self.send_char(charnum)

    def specialUnfancyKey(self, charnum):
        """
        Field special keys not mapped by fancykeymap.
        This is used for the arrow keys for local history management.
        """
        if self.local_recall:
            lh = len(self.history_buffer)
            phl = self.history_level
            # Handle moving to new history lines.
            if charnum == Qt.Key_Up:
                # Move to one earlier history line.
                self.history_level += 1
                self.history_level = min( self.history_level, lh-1 )
            elif charnum == Qt.Key_Down:
                # Move to one later history line (exit history recall if history level reaches -1).
                self.history_level -= 1
                self.history_level = max( self.history_level, -1 )
            # If moved to a new history line, set cursor to the end of that line.
            if (charnum == Qt.Key_Up) or (charnum == Qt.Key_Down):
                self.edit_offset = 0
                self.set_cursor_char_offset(self.edit_offset)
            # If still in history recall ...
            if self.history_level > -1:
                # Handle moving left and right in a history line when editing it.
                if self.editing:
                    viewing_line = self.history_line
                else:
                    viewing_line = self.history_buffer[lh-self.history_level-1]
                ls = len(viewing_line)
                if charnum == Qt.Key_Left:
                    self.edit_offset += 1
                    self.edit_offset = min( ls, self.edit_offset )
                    self.set_cursor_char_offset(self.edit_offset)
                elif charnum == Qt.Key_Right:
                    self.edit_offset -= 1
                    self.edit_offset = max( 0, self.edit_offset )
                    self.set_cursor_char_offset(self.edit_offset)
                # Display the selected history line.
                self.screenClearLine()
                self.screenAddCodesArray(viewing_line)
            # No longer in history recall. If previouly in it, clear the current line display.
            else:
                if phl > -1:
                    self.screenClearLine(True)
            
    def event(self,event):
        """
        Intercept all events here to capture TAB key events and prevent
        TAB from switching focus to other widgets. Instead, send a TAB to the host.
        This is also where 'hot keys' are defined. These need Alt+<key> pressed.
        """
        if self.debuglevel > 2:
            print('event() event =',event)
        altkeymap = {Qt.Key_G:1,Qt.Key_T:2,Qt.Key_K:3,Qt.Key_U:4,Qt.Key_D:5,Qt.Key_H:6,
                     Qt.Key_PageUp:4,Qt.Key_PageDown:5,Qt.Key_Home:6,Qt.Key_A:7}
        spckeymap = {Qt.Key_PageUp:4,Qt.Key_PageDown:5,Qt.Key_Home:6}
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Tab:
                self.send_char(9)
                return True
            if key == Qt.Key_Insert:
                self.send_char(10)
                return True
            if key in spckeymap:
                if self.userwidget is not None:
                    try:
                        self.userwidget.alt_key_handler(spckeymap[key])
                    except:
                        print('Failed to call userwidget.alt_key_handler()')
                return True
            if self.alt:
                if key in altkeymap:
                    if self.userwidget is not None:
                        try:
                            self.userwidget.alt_key_handler(altkeymap[key])
                        except:
                            print('Failed to call userwidget.alt_key_handler()')
                    return True
        return GTermWidget.event(self,event)

    
###################
# AudioFile CLASS #
#  For a "bell"!  #
###################

class AudioFile:
    """
    Play a WAV format audio file with PyAudio.
    """
    chunk = 1024
    def __init__(self, file):
        """
        Init audio stream
        """ 
        self.wf = wave.open(file, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True
        )

    def play(self):
        """
        Play entire file 
        """
        data = self.wf.readframes(self.chunk)
        #print('frame length =',len(data))
        while len(data) > 0:
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)

    def close(self):
        """
        Graceful shutdown
        """
        time.sleep(0.2) # Apparently this is needed ... 
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

def make_noise(wavfile):
    """
    Make an arbitrary sound by playing a specified WAV file.
    """
    a = AudioFile(wavfile)
    a.play()
    a.close()

#################################
# MAIN PROGRAM                  #
# PySide2 GUI terminal program. #
#################################

if __name__ == '__main__':

    def dumpChar(c,simple=False):
        """
        Make a printable representation of character c.
        """
        cch=["NUL","SOH","STX","ETX","EOT","ENQ","ACK","BEL",
             " BS"," HT"," LF"," VT"," FF"," CR"," SO"," SI",
             "DLE","DC1","DC2","DC3","DC4","NAK","SYN","ETB",
             "CAN"," EM","SUB","ESC"," FS"," GS"," RS"," US"]
        out = ''
        if type(c) == int:
            oc = c
        else:
            oc = ord(c)
        if oc > 31 and oc < 127:
            if simple:
                out += c
            else:
                out += '{0:02x} ({1})'.format(oc,c)
        else:
            if oc < 127:
                out += '{0:02x} {1}'.format(oc,cch[oc])
            elif oc > 127:
                out += '{0:02x} HIB'.format(oc)
            else:
                out += '{0:02x} DEL'.format(oc)
        return out

    def dumpData(string):
        """
        Display character data for debugging purposes.
        """
        i = 0
        out = ''
        for c in string:
            out += dumpChar(c)
            if i != (len(string)-1):
                out += ', '
            if ((i+1)%8) == 0:
                print(out)
                out = ''
            i += 1
        if len(out) > 0:
            print(out)
        print('====')

    def dumpString(string):
        """
        Return a string containing representation of each character in input string.
        """
        i = 0
        out = '|'
        for c in string:
            out += dumpChar(c,True)
            if i != (len(string)-1):
                out += '|'
        return out

    def yns(logical):
        """
        Return string On or Off reflecting boolean logical.
        """
        if( logical ):
            return "On"
        else:
            return "Off"

    # Cyber APL 2 batch codes to extended character number map.
    cyber_apl_in_map = \
        {'$ml':200,'$dv':146,'$mx':198,'$mn':197,'$lg':254,
         '$md':124,'$ci':195,'$ne':194,'$tl':126,'$le':193,
         '$ge':192,'$an':191,'$or':190,'$nd':189,'$nr':188,
         '$ro':187,'$cn':186,'$io':185,'$xd':184,'$ep':183,
         '$ug':182,'$dg':181,'$dl':180,'$sm':178,'$bt':179,
         '$ta':177,'$dr':176,'$rt':149,'$ru':158,'$bv':150,
         '$rp':151,'$ev':152,'$fm':153,'$nl':255,'$tp':154,
         '$is':160,'$qd':156,'$qp':157,'$bc':162,'$ld':159,
         '$go':155,'$lp':161,'$du':163,'$di':166,'$ng':174
         }

    def cyber_apl_escape(char,ichar,escapeseq,numescape):
        """
        Map Cyber APL 2 batch sequences to our extended character set.
        """
        #print "***apl_escape called."
        escapeseq.append(ichar)
        numescape += 1
        if numescape == 3:
            numescape = 0
            #print numescape, escapeseq
            try:
                keystr = ''
                for c in escapeseq:
                    keystr += chr(c)
                repl = []
                repl.append(cyber_apl_in_map[keystr.lower()])
                return (False,repl,numescape,False)
            except:
                return (False,escapeseq,numescape,False)
        else:
            #print numescape, escapeseq
            return (True,None,numescape,False)

    def reverse_dict_kv(indict):
        """
        Swap keys and values in a dictionary.
        """
        outdict = {}
        for key,val in list(indict.items()):
            outdict[val] = key
        return outdict

    def ansi_escape(char,ichar,escapeseq,numescape):
        """
        Handle (or just discard) ANSI escape sequences.
        """
        ansiendchars = ['A','B','C','D','E','F','G','H','J','K','S',
                        'T','f','m','n','s','u','l','h','z','Z']
        #print "***ansi_escape called."
        escapeseq.append(ichar)
        numescape += 1
        # First char (the esc). Stay in escape mode.
        if numescape == 1:
            return (True,None,numescape,False)
        # Second char. Should be [ for ANSI seq. (CSI).
        # If not, exit escape mode. Return the characters sos they can be used as normal.
        elif numescape == 2:
            #print char
            if char != '[':
                numescape = 0
                return (False,escapeseq,numescape,False)
            else:
                return(True,None,numescape,False)
        # Third ... Accumulate sequence until a known sequence end char is found.
        else:
            if char in ansiendchars:
                #for c in escapeseq:
                #    print c
                numescape = 0
                # If it is our own graphics extension sequence, process it.
                # Otherwise, just throw it away for now.
                if char == 'z' or char == 'Z':
                    return(False,escapeseq,numescape,True)
                else:
                    return(False,None,numescape,False)
            else:
                return(True,None,numescape,False)

    def cyber_apl_graphics_escape(char,ichar,escapeseq,numescape):
        """
        Handle CDC Cyber APL 2 graphics escape sequences.
        """
        ansiendchars = ['@']
        #print "***cyber_apl_graphics_escape called."
        escapeseq.append(ichar)
        numescape += 1
        # First char (the esc). Stay in escape mode.
        if numescape == 1:
            return (True,None,numescape,False)
        # Second char. Should be [ here. 
        # If not, exit escape mode. Return the characters so they can be used as normal.
        elif numescape == 2:
            #print char
            if char != '[':
                numescape = 0
                return (False,escapeseq,numescape,False)
            else:
                return(True,None,numescape,False)
        # Third ... Accumulate sequence until a known sequence end char is found.
        else:
            if char in ansiendchars:
                #for c in escapeseq:
                #    print c
                numescape = 0
                # It must be our own graphics extension sequence, process it.
                return(False,escapeseq,numescape,True)
            else:
                return(True,None,numescape,False)            

    class TerminalDialog(QDialog):
        """
        Complete GUI Telnet client using a glass teletype model.
        """
        def __init__(self,parent=None):
            super(TerminalDialog,self).__init__(parent)
            # Try to have the dialog show a minimize icon.
            windowflags = Qt.Window | Qt.WindowSystemMenuHint | \
                Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
            self.setWindowFlags(windowflags)
            ouriconname = get_application_file_name( 'gterm', 'gtermicon.png' )
            self.setWindowIcon( QIcon( ouriconname ) )
            self.setWindowTitle('GTerm')
            # Log file name and location.
            self.lfname = ''
            self.logdir = '/tmp' #  '.'
            # Telnet terminal widget.
            self.screen = GTermTelnetWidget(charsetname='mainfonttexture',vkbname='aplvkb',\
                                                umapname='mainfontunicode' )
            self.screen.setFocus()
            self.screen.set_debuglevel(0)
            self.screen.set_userwidget(self)
            # Escape sequence processor. Compatible with default localhost unix mode.
            self.mode(3)
            # Send DEL for backspace key
            self.screen.backspaceSendsDelete(True)
            # Open and parse the host data file.
            self.read_host_data()
            # First horizontal group of PyQt widgets.
            self.showVkbCheckBox = QCheckBox("Show keyboard")
            self.showNonPrintCheckBox = QCheckBox("Show non-print")
            self.localEchoCheckBox = QCheckBox("Local echo")
            self.debugCheckBox = QCheckBox("Debug")
            self.modeComboBox = QComboBox()
            self.modeComboBox.addItems(["Cyber/APL","Cyber","VMS","Unix","Unix/Alt","Windows"])
            self.modeComboBox.setCurrentIndex(3) # Make default Unix to match local host.
            self.viewComboBox = QComboBox()
            self.viewComboBox.addItems(["Text","Graphics"])
            self.ffClearsCheckBox = QCheckBox("FF clears")
            self.onPaperCheckBox = QCheckBox("On paper")
            self.noEscapeCheckBox = QCheckBox("No escape")
            checkboxLayout = QHBoxLayout()
            checkboxLayout.addWidget(self.modeComboBox)
            checkboxLayout.addWidget(self.showVkbCheckBox)
            checkboxLayout.addWidget(self.showNonPrintCheckBox)
            checkboxLayout.addWidget(self.localEchoCheckBox)
            checkboxLayout.addWidget(self.debugCheckBox)
            checkboxLayout.addWidget(self.ffClearsCheckBox)
            checkboxLayout.addWidget(self.onPaperCheckBox)
            checkboxLayout.addWidget(self.noEscapeCheckBox)
            checkboxLayout.addWidget(self.viewComboBox)
            # Second horizontal group of PyQt widgets.
            # Set default host to be localhost, port 23, unix mode.
            self.hostAddressEdit = QLineEdit("localhost")
            self.portNumberSpinbox = QSpinBox()
            self.portNumberSpinbox.setRange(1,99999)
            self.portNumberSpinbox.setValue(23)
            self.connectPushButton = QPushButton("Connect")
            self.clearPushButton = QPushButton("Clear")
            self.logRenameButton = QPushButton("Save log")
            self.saveGrafButton = QPushButton("Save graphics")
            self.hostsComboBox = QComboBox()
            for hostrecord in self.hostinfo:
                self.hostsComboBox.addItem(hostrecord[0])
            labelhosts = QLabel("To:")
            self.guideComboBox = QComboBox()
            self.guideComboBox.addItems(["No guide","Fortran"])
            self.statusButton = QPushButton("Status")
            buttonLayout = QHBoxLayout()
            buttonLayout.addWidget(self.hostAddressEdit)
            buttonLayout.addWidget(self.portNumberSpinbox)
            buttonLayout.addWidget(self.connectPushButton)
            buttonLayout.addWidget(labelhosts)
            buttonLayout.addWidget(self.hostsComboBox)
            buttonLayout.addWidget(self.clearPushButton)
            buttonLayout.addWidget(self.logRenameButton)
            buttonLayout.addWidget(self.saveGrafButton)
            buttonLayout.addWidget(self.guideComboBox)
            buttonLayout.addWidget(self.statusButton)
            # Assemble the groups vertically
            layout = QVBoxLayout()
            layout.addWidget(self.screen)
            layout.addLayout(buttonLayout)
            layout.addLayout(checkboxLayout)
            self.setLayout(layout)
            # Connect event handlers
            self.connectPushButton.clicked.connect(self.connecthost)
            self.clearPushButton.clicked.connect(self.clear)
            self.showVkbCheckBox.stateChanged.connect(self.showvkb)
            self.localEchoCheckBox.stateChanged.connect(self.localecho)
            self.debugCheckBox.stateChanged.connect(self.debugon)
            self.modeComboBox.currentIndexChanged.connect(self.mode)
            self.viewComboBox.currentIndexChanged.connect(self.view)
            self.logRenameButton.clicked.connect(self.renamelog)
            self.saveGrafButton.clicked.connect(self.savegraf)
            self.ffClearsCheckBox.stateChanged.connect(self.ffmode)
            self.onPaperCheckBox.stateChanged.connect(self.onpaper)
            self.hostsComboBox.currentIndexChanged.connect(self.selectknownhost)
            self.statusButton.clicked.connect(self.showstatus)
            self.guideComboBox.currentIndexChanged.connect(self.guide)
            self.noEscapeCheckBox.stateChanged.connect(self.noescapemode)

            #self.screen.connect(self.screen,SIGNAL("knownAltKey(int)"),self.alt_key_handler)

        def alt_key_handler(self,kcode):
            """
            Handle special Alt key combinations as defined in GTermTelnetWidget.event().
            """
            if kcode == 1:   # t: go to text view
                self.viewComboBox.setCurrentIndex(1)
            elif kcode == 2: # g: go to graphics view
                self.viewComboBox.setCurrentIndex(0)
            elif kcode == 3: # k: toggle virtual keyboard state.
                self.showVkbCheckBox.nextCheckState()
            elif kcode == 4: # u: scroll up 20 lines OR PgUp
                self.screen.deltaScroll(20)
            elif kcode == 5: # d: scroll down 20 lines OR PgDn
                self.screen.deltaScroll(-20)
            elif kcode == 6: # h: no scroll OR Home
                self.screen.setScroll(0)
                self.screen.clearModifiers()
                

        def read_host_data(self):
            """
            Get information on known host systems.
            """
            self.hostinfo = [['localhost','localhost',23,'unix']]
            try:
                ourhostinfo = get_application_file_name( 'gterm', 'gtermhostinfo.txt' )
                flun = open(ourhostinfo,'r')
                linenum = 0
                for line in flun:
                    linenum += 1
                    if line[0] != '#':
                        words = line.rstrip().split()
                        if len(words) == 4:
                            try:
                                words[2] = int(words[2])
                                self.hostinfo.append(words)
                            except:
                                print('*** ERROR: hostinfo: expected integer port number at line:',linenum)
                        else:
                            print('*** ERROR: hostinfo: expected 4 words on line. At line:',linenum)
                flun.close()
                #print self.hostinfo
            except:
                print('*** WARNING: Failed to read gtermhostinfo.txt')

        def logfilename(self):
            """
            Generate a log file name from the current time and date.
            """
            localtime = time.localtime(time.time())
            tstring = 'gterm_log_{0:04d}_{1:02d}_{2:02d}_{3:02d}_{4:02d}_{5:02d}.utxt'.\
                format(localtime.tm_year,localtime.tm_mon,localtime.tm_mday,\
                           localtime.tm_hour,localtime.tm_min,localtime.tm_sec)
            self.lfname = os.path.abspath(os.path.join(self.logdir,tstring))

        def connecthost(self):
            """
            Connect to host - but only if not already connected.
            """
            self.logfilename()
            if not self.screen.haveconnection:
                self.screen.clearScreen()
                self.screen.open_conn(str(self.hostAddressEdit.text()), self.portNumberSpinbox.value())
                self.screen.openLogFile(self.lfname)

        def selectknownhost(self,ihost):
            """
            Choose the known host to connect to.
            """
            hostrecord = self.hostinfo[ihost]
            self.hostAddressEdit.setText(hostrecord[1])
            self.portNumberSpinbox.setValue(hostrecord[2])
            typename_to_index = {'nosapl':0,'nos':1,'vms':2,'unix':3,'unixalt':4,'windows':5}
            try:
                imode = typename_to_index[hostrecord[3]]
            except:
                imode = 3
            self.mode(imode)
            self.modeComboBox.setCurrentIndex(imode)

        def clear(self):
            """
            Clear the screen.
            """
            self.screen.clearScreen()

        def setlogdir(self,logfiledir):
            """
            Set the directory to keep log files in.
            """
            self.logdir = logfiledir

        def renamelog(self):
            """
            Close the log file, rename it and open a new log file.
            """
            fname = QFileDialog.getSaveFileName(self,'Save log',os.getenv('HOME'))
            try:
                fname = fname[0]
                if len(fname) > 0:
                    self.screen.closeLogFile()
                    shutil.move(self.lfname,str(fname))
                    self.logfilename()
                    self.screen.openLogFile(self.lfname)
            except Exception as e:
                print('renamelog(): Do not understand:',self.lfname,str(fname))
                print('... reason:',e)

        def savegraf(self):
            """
            Save graphics to SVG format file.
            """
            fname = QFileDialog.getSaveFileName(self,'Save graphics',os.getenv('HOME'))
            try:
                fname = fname[0]
                if len(fname) > 0:
                    self.screen.saveGraphics(str(fname))
            except Exception as e:
                print('savegraf(): Do not understand:',str(fname))
                print('... reason:',e)

        def showvkb(self):
            """
            Show the virtual keyboard.
            """
            self.screen.set_showvkb(self.showVkbCheckBox.isChecked())

        def nonprint(self):
            """
            Show non-printing characters.
            """
            self.screen.set_shownonprint(self.showNonPrintCheckBox.isChecked())

        def localecho(self):
            """
            Do local echo.
            """
            self.screen.set_local_echo(self.localEchoCheckBox.isChecked())

        def debugon(self):
            """
            Turn debug output on or off.
            """
            if self.debugCheckBox.isChecked():
                self.screen.set_debuglevel(10)
            else:
                self.screen.set_debuglevel(0)

        def ffmode(self):
            """
            Clear text on form feed. Or not.
            """
            self.screen.setFFMode(self.ffClearsCheckBox.isChecked())

        def onpaper(self):
            """
            Turn on green bar paper background. Or not.
            """
            self.screen.setOnPaper(self.onPaperCheckBox.isChecked())

        def noescapemode(self):
            """
            Turn off escape processing to allow esacpe character to be typed in.
            """
            self.screen.set_escape_on_off(self.noEscapeCheckBox.isChecked())

        def set_arrow_keys(self):
            """
            ANSI arrow key code definitions.
            """
            self.screen.fancykeymap[Qt.Key_Up] = '\033[A'
            self.screen.fancykeymap[Qt.Key_Down] = '\033[B'
            self.screen.fancykeymap[Qt.Key_Right] = '\033[C'
            self.screen.fancykeymap[Qt.Key_Left] = '\033[D'

        def mode(self,imode):
            """
            Operating mode.
            """
            if imode == 0:
                # Cyber/APL mode.
                self.screen.fancykeymap.clear()
                self.screen.clearEscapeProcessors()
                self.screen.setEscapeProcessFunc('$',cyber_apl_escape)
                self.screen.setEscapeProcessFunc('@',cyber_apl_graphics_escape)
                self.screen.backspaceSendsDelete(False)
                self.screen.followBackspaceWithNewline(True)
                self.screen.char_to_string_map = reverse_dict_kv(cyber_apl_in_map)
                # Define a string to send if F1 key is pressed.
                self.screen.fancykeymap[Qt.Key_F1] = 'APL,TT=713.\r'
                self.screen.set_terminate_char(20) # Ctrl-T
                self.screen.set_local_recall(True)
            elif imode == 1:
                # Cyber without APL mode.
                self.screen.fancykeymap.clear()
                self.screen.clearEscapeProcessors()
                self.screen.setEscapeProcessFunc(chr(0x1b),ansi_escape)
                self.screen.backspaceSendsDelete(False)
                self.screen.followBackspaceWithNewline(False)
                # Define a string to send if F2 key is pressed.
                self.screen.fancykeymap[Qt.Key_F2] = 'ABGPLOT,OBEY=APLOT,GET=Y.\r'
                self.screen.set_terminate_char(20) # Ctrl-T
                self.screen.set_local_recall(True)
            elif imode == 2:
                # VMS mode.
                self.screen.fancykeymap.clear()
                self.screen.clearEscapeProcessors()
                self.screen.setEscapeProcessFunc(chr(0x1b),ansi_escape)
                self.screen.backspaceSendsDelete(True)
                self.screen.followBackspaceWithNewline(False)
                # Define a string to send if F1 key is pressed.
                self.screen.fancykeymap[Qt.Key_F1] = 'set term/echo/unknown\r'
                # Define strings for the arrow keys (VT100 strings)
                self.set_arrow_keys()
                self.screen.set_terminate_char(25) # Ctrl-Y
                self.screen.set_local_recall(False)
            elif imode == 3:
                # Unix mode.
                self.screen.fancykeymap.clear()
                self.screen.clearEscapeProcessors()
                self.screen.setEscapeProcessFunc(chr(0x1b),ansi_escape)
                self.screen.backspaceSendsDelete(True)
                self.screen.followBackspaceWithNewline(False)
                # Define strings for the arrow keys (VT100 strings)
                self.set_arrow_keys()
                self.screen.set_terminate_char(3) # Ctrl-C
                self.screen.set_local_recall(False)
            elif imode == 4:
                # Unix mode / Alt graphics.
                self.screen.fancykeymap.clear()
                self.screen.clearEscapeProcessors()
                self.screen.setEscapeProcessFunc(chr(0x1b),ansi_escape)
                self.screen.setEscapeProcessFunc('@',cyber_apl_graphics_escape)
                self.screen.backspaceSendsDelete(True)
                self.screen.followBackspaceWithNewline(False)
                # Define strings for the arrow keys (VT100 strings)
                self.set_arrow_keys()
                self.screen.set_terminate_char(3) # Ctrl-C
                self.screen.set_local_recall(False)
            elif imode == 5:
                # Windows mode.
                self.screen.fancykeymap.clear()
                self.screen.clearEscapeProcessors()
                self.screen.setEscapeProcessFunc(chr(0x1b),ansi_escape)
                self.screen.backspaceSendsDelete(False)
                self.screen.followBackspaceWithNewline(False)
                # Define strings for the arrow keys (VT100 strings)
                self.set_arrow_keys()
                self.screen.set_terminate_char(3) # Ctrl-C
                self.screen.set_local_recall(False)
                
        def view(self,iview):
            """
            View text or graphics.
            """
            if iview == 0:
                self.screen.viewText()
            elif iview == 1:
                self.screen.viewGraphics()

        def guide(self,iguide):
            """
            Show a horizontal position guide. Or not.
            """
            guides = [ [], [6,72,80] ] # None, Fortran, ...
            try:
                guide_pos = guides[iguide]
            except:
                guide_pos = []
            self.screen.set_horizontal_guide( guide_pos )
                
        def showstatus(self):
            """
            Show status dialog.
            """
            sp3 = '&nbsp;&nbsp;&nbsp;'
            sp6 = sp3 + sp3
            fancykeynames = {Qt.Key_F1:'F1',Qt.Key_F2:'F2',Qt.Key_F3:'F3',Qt.Key_F4:'F4',
                             Qt.Key_F5:'F5',Qt.Key_F6:'F6',Qt.Key_F7:'F7',Qt.Key_F8:'F8',
                             Qt.Key_F9:'F9',Qt.Key_F10:'F10',Qt.Key_F11:'F11',Qt.Key_F12:'F12',
                             Qt.Key_F13:'F13',Qt.Key_F14:'F14',Qt.Key_F15:'F15',Qt.Key_F16:'F16',
                             Qt.Key_Up:'Up Arrow',Qt.Key_Down:'Down Arrow',
                             Qt.Key_Left:'Left Arrow',Qt.Key_Right:'Right Arrow'}
            smsg = "<font color=red size=14><b>GTerm Status Information:</b></font><br>"
            smsg += "{0}<b>Version information:</b><br>".format(sp3)
            smsg += "{0}Version: {1}<br>".format(sp6,_current_git_desc)
            smsg += "{0}Git HEAD: {1}<br>".format(sp6,_current_git_hash)
            try:
                buildtime = time.ctime(os.path.getmtime(__file__))
                smsg += "{0}GTerm script (apparently) last modified: {1}<br>".format(sp6,buildtime)
            except:
                pass
            smsg += "{0}Author: Nick Glazzard (nick@hccc.org.uk)<br>".format(sp6)
            smsg += "{0}<b>Window Geometry:</b><br>".format(sp3)
            widthchars = int((self.screen.viewport[0]-self.screen.xmargin)/self.screen.charspace)
            heightchars = int((self.screen.viewport[1]-self.screen.ymargin)/self.screen.linespace)
            smsg += "{0}Width = {1} pixels, {3} chars, Height = {2} pixels, {4} lines.<br>".\
                format(sp6,self.screen.width_pixels,self.screen.height_pixels,widthchars,heightchars)
            smsg += "{0}Aspect ratio = {1}<br>".format(sp6,self.screen.aspect)
            smsg += "{0}<b>Configuration files:</b><br>".format(sp3)
            smsg += "{0}Character texture map: {1} (.jsn/.png)<br>".format(sp6,self.screen.save_charsetname)
            smsg += "{0}Virtual keyboard map: {1} (.jsn/.png)<br>".format(sp6,self.screen.save_vkbname)
            smsg += "{0}Unicode log file map: {1} (.jsn)<br>".format(sp6,self.screen.save_umapname)
            smsg += "{0}Bell sound WAV file: {1}<br>".format(sp6,self.screen.bell_wav)
            smsg += "{0}<b>Modifier states:</b><br>".format(sp3)
            smsg += "{0}Shift: {1}, ShiftLock: {2}, Control: {3}, Alt: {4}<br>".\
                format(sp6,yns(self.screen.shift),yns(self.screen.shiftlock),yns(self.screen.ctrl),yns(self.screen.alt))
            smsg += "{0}<b>Terminate character: {1}</b><br>".format(sp3,dumpChar(chr(self.screen.terminate_char)))
            smsg += "{0}<b>Number of fancy keys defined: {1}</b><br>".format(sp3,len(self.screen.fancykeymap))
            if len(self.screen.fancykeymap) > 0:
                for k in list(self.screen.fancykeymap.keys()):
                    try:
                        kname = fancykeynames[k]
                    except:
                        kname = 'Unknown'
                    smsg += "{0}Key:{1} = {2}<br>".format(sp6,kname,dumpString(self.screen.fancykeymap[k]))
            smsg += "{0}<b>Number of escape processors defined: {1}</b><br>"\
                .format(sp3,len(self.screen.escapeProcessFuncList))
            if len(self.screen.escapeProcessFuncList) > 0:
                for i in range(0,len(self.screen.escapeProcessFuncList)):
                    (ec,epf) = self.screen.escapeProcessFuncList[i]
                    smsg += "{0}{1}: {2}<br>".format(sp6,i+1,epf.__name__)
            smsg += "{0}<b>Number of incoming single character mappings defined: {1}</b><br>"\
                .format(sp3,len(self.screen.incharmap))
            if len(self.screen.incharmap) > 0:
                i = 1
                for k in list(self.screen.incharmap.keys()):
                    smsg += "{0}{1}: {2} -> {3}<br>"\
                        .format(sp6,i,dumpChar(chr(k),True),dumpChar(chr(self.screen.incharmap[k]),True))
                    i += 1
            smsg += "{0}<b>Number of outgoing single character mappings defined: {1}</b><br>"\
                .format(sp3,len(self.screen.outcharmap))
            if len(self.screen.outcharmap) > 0:
                i = 1
                for k in list(self.screen.outcharmap.keys()):
                    smsg += "{0}{1}: {2} -> {3}<br>"\
                        .format(sp6,i,dumpChar(chr(k),True),dumpChar(chr(self.screen.outcharmap[k]),True))
                    i += 1
            if self.screen.char_to_string_map == None:
                ncsm = 0
            else:
                ncsm = len(self.screen.char_to_string_map)
            smsg += "{0}<b>Number of character to string mappings: {1}</b><br>"\
                .format(sp3,ncsm)
            smsg += "{0}<b>Telnet connection: {1}</b><br>".format(sp3,yns(self.screen.haveconnection))
            if self.screen.haveconnection:
                smsg += "{0}Connected since: {1}<br>".format(sp6,self.screen.connect_time)
            smsg += "{0}<b>Text plane state:</b><br>".format(sp3)
            smsg += "{0}Maximum buffer size = {1} lines.<br>".format(sp6,self.screen.maxlines)
            smsg += "{0}Number of lines currently in buffer = {1}<br>".format(sp6,len(self.screen.screen))
            smsg += "{0}Visible region scroll = {1} lines<br>".format(sp6,self.screen.scroll)
            smsg += "{0}<b>Graphics plane state:</b><br>".format(sp3)
            smsg += "{0}Commands in graphics buffer = {1}<br>".format(sp6,self.screen.gcbcmds)

            # Display it. Use a label in a scrollable area.
            self.statLabel = QLabel(smsg)
            self.scrollArea = QScrollArea()
            self.scrollArea.setGeometry(QRect(10,10,550,650))
            self.scrollArea.setWidgetResizable(True)
            self.scrollArea.setWindowTitle("GTerm Help and Status")
            self.scrollAreaWidgetContents = QWidget()
            self.scrollAreaWidgetContents.setGeometry(QRect(10,10,550,650))
            self.scrollArea.setWidget(self.statLabel)
            self.scrollArea.show()

        def closeEvent(self, event):
            """
            Intercept close program event.
            """
            quit_msg = "Exit GTerm?"
            reply = QMessageBox.question(self, 'GTerm Exit Warning', quit_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                # If there is an open connection, close it so the server end disconnects.
                # The read input thread is still running and will not like this, but ...
                if self.screen.haveconnection:
                    try:
                        self.screen.telnet.close()
                    except:
                        pass
                event.accept()
            else:
                event.ignore()

    # Main line
    if sys.platform.startswith('darwin'):
        pass
    else:
        QCoreApplication.setAttribute(Qt.AA_X11InitThreads)
    app = QApplication(["GTerm: Glass Teletype with Graphics!"])
    dialog = TerminalDialog()
    dialog.setlogdir("/tmp") #os.path.join(os.getcwd(),"LogFiles"))
    dialog.show()
    app.exec_()
