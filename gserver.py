#!/usr/bin/env python3
"""
"""

from socket import *
import threading
import queue
import time
import numpy as np
import sys
import errno

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

class GServerCommand(object):
    """ 
    Define commands that can be sent to the GServerThread server.
    START:    No data.
    SEND:     Bytes to send.
    RECV:     No data.
    """
    START, SEND, RECV  = list(range(3))

    def __init__(self, type, data=None):
        self.type = type
        self.data = data

class GServerMessage(object):
    """ 
    Define messages that the GServerThread server can put on its output queue.
    N.B. The server's output queue is the input to the software that uses GServerThread.
         ERROR:    Error message string.
         SUCCESS:  Received data.
    """
    ERROR, SUCCESS = list(range(2))

    def __init__(self, type, data=None):
        self.type = type
        self.data = data

class GServerThread(threading.Thread):
    """ 
    A simple TCP/IP server that GTerm can connect to. Once it is running and a connection has been
    made, commands sent over a Queue (cmdq) can send data to GTerm and data from GTerm can be delivered
    to a second Queue (outq). This allows GTerm to be used from a program without data going via stdin
    and stdout.
    The use of Queues is because this TCP/IP server must run on a separate thread to avoid unwanted
    blocking i/o.
    """

    def __init__(self, cmdq, outq, port=51234, debuglevel=0):
        """
        Constructor. Prepare to run a thread.
        """
        super(GServerThread,self).__init__()
        self.cmdq = cmdq
        self.outq = outq
        self.alive = threading.Event()
        self.alive.set()
        self.socket = None
        self.port = port
        self.retdata = None
        self.daemon = True # This thread will not prevent Python exiting, if it is the last thread running.
        self.server_running = False
        self.gterm_connected = False
        self.debuglevel = debuglevel
        if self.debuglevel > 1:
            print('GserverThread.__init__() returning.')

    def run(self):
        """
        When the thread starts, wait for a START command. 
        When received, run the server code (that never returns).
        """
        if self.debuglevel > 1:
            print('GserverThread.run()')
        while self.alive.isSet():
            try:
                cmd = self.cmdq.get(True)
                if self.debuglevel > 1:
                    print('GserverThread.run() got cmd')
                if cmd == GServerCommand.START:
                    if self.debuglevel > 1:
                        print('GserverThread.run() got START')
                    self.server()
                else:
                    continue
            except queue.Empty as e:
                continue
            
    def join(self,timeout=None):
        """
        Wait for the thread to end. It won't, and this is not used.
        """
        self.alive.clear()
        threading.Thread.join(self,timeout)

    def server(self):
        """
        Implement a minimal TCP/IP server to communicate bi-directionally with a GTerm instance.
        """
        if self.debuglevel > 1:
            print('GserverThread.server() called.')
            
        # Start listening for a client connection.
        try:
            sockobj = socket(AF_INET, SOCK_STREAM)
            # Try to avoid 'address already in use' errors.
            sockobj.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            # Try to get messages actually sent promptly by disabling the Nagel algorithm. Seems to help.
            sockobj.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
            sockobj.bind(('', self.port))
            sockobj.listen(2)
        except Exception as e:
            print('Failed to set up server.')
            print('... reason:',e)
            self.server_running = False

        # Set server running flag.
        self.server_running = True

        # Loop forever ...
        while True:
            if self.debuglevel > 1:
                print('GserverThread.server() waiting for connection.')
            
            # Wait for a connection.
            self.socket, address = sockobj.accept()
            if self.debuglevel > 1:
                print( 'GServer connected to from:', address)
            self.gterm_connected = True

            while True:

                # Try to get a command from the command queue.
                if self.debuglevel > 1:
                    print('... about to wait for a command ...')
                try:
                    cmd = self.cmdq.get(True)
                    if self.debuglevel > 1:
                        print('GserverThread.server() got cmd.')
                        print('type(cmd):',type(cmd))
                        print('cmd:',cmd.type)
                    
                    # Send data to GTerm?
                    if cmd.type == GServerCommand.SEND:
                        if self.debuglevel > 1:
                            print('GserverThread.server() got SEND cmd.')
                        try:
                            self.socket.send(_strtobytes(cmd.data))
                        except OSError as e:
                            print('Failed to SEND data to GTerm.')
                            print('... reason:', e)
                            if (e.errno == errno.EPIPE) or (e.errno == errno.ESHUTDOWN):
                                print('... GTerm has probably been closed. Will await new connection.')
                                try:
                                    self.socket.close()
                                except:
                                    pass
                                break

                    # Get data from GTerm?
                    elif cmd.type == GServerCommand.RECV:
                        if self.debuglevel > 1:
                            print('GserverThread.server() got RECV cmd.')
                        try:
                            returned_data = self.socket.recv(4096)
                            self.outq.put(self._data_out(returned_data))
                        except:
                            print('Failed to RECV data from GTerm.')
                            self.outq.put(self._error_out('$$$ERROR$$$'))

                    # Something that should not be.
                    else:
                        print('Unknown command!')
                        continue

                # Try again if empty command queue.
                except queue.Empty as e:
                    continue

    def _error_out(self, errorstring):
        return GServerMessage(GServerMessage.ERROR, errorstring)

    def _data_out(self, data=None):
        return GServerMessage(GServerMessage.SUCCESS, data)

class GTermComms(object):
    """
    Create and start a GServerThread server then communicate with it and hence with any
    connected GTerm.
    """

    def __init__(self, port=51234, debuglevel=0):
        super(GTermComms,self).__init__()
        self.debuglevel = debuglevel
        self.cmdq = queue.Queue()
        self.outq = queue.Queue()
        self.gserver = GServerThread(self.cmdq, self.outq, port=port)
        self.gserver.start()
        self.cmdq.put(GServerCommand.START)

    def _is_ready(self):
        if not self.gserver.server_running:
            print('GTermComms: server is not running. Probably a fatal error.')
            return False
        if not self.gserver.gterm_connected:
            print('GTermComms: No GTerm is connected yet.')
            return False
        return True

    def send(self, data):
        if self._is_ready():
            self.cmdq.put(GServerCommand(GServerCommand.SEND, data))
            return True
        else:
            return False

    def receive(self, timeout=None):
        if self._is_ready():
            self.cmdq.put(GServerCommand(GServerCommand.RECV))
            try:
                received = self.outq.get(True, timeout=timeout)
            except queue.Empty as e:
                if self.debuglevel > 1:
                    print('receive(): time out.')
                return None
            if received.type == GServerMessage.ERROR:
                if self.debuglevel > 1:
                    print('receive(): recv() error.')
                return None
            else:
                return _bytestostr(received.data)
        else:
            return None

class GTermLib(object):
    """
    Drawing library for GTerm.
    """

    def __init__(self, port=51234, debuglevel=0):
        self.comms = GTermComms(port=port, debuglevel=debuglevel)

    def ready(self):
        return self.comms._is_ready()

    def clamp(self,v,lo,hi):
        return max(lo,min(v,hi))

    def clear(self):
        return self.comms.send('@[0@')

    def colour(self,r,g,b):
        ir = self.clamp(r,0.0,1.0)
        ig = self.clamp(g,0.0,1.0)
        ib = self.clamp(b,0.0,1.0)
        s = '@[1 {0:.3f} {1:.3f} {2:.3f} @'.format(ir,ig,ib)
        return self.comms.send(s)

    def erase(self):
        return self.comms.send('@[2@')

    def pen(self,x,y,z):
        if z > 0:
            c = 4
        else:
            c = 3
        s = '@[{0} {1} {2} @'.format(c,x,y)
        return self.comms.send(s)

    def move(self,x,y):
        return self.pen(x,y,0)

    def draw(self,x,y):
        return self.pen(x,y,1)

    def flush(self):
        return self.comms.send('@[5@')        

    def width(self,w):
        iw = self.clamp(w,0.0,9.0)
        s = '@[6 {0} @'.format(iw)
        return self.comms.send(s)

    def bounds(self,xlo,ylo,xhi,yhi):
        s = '@[7 {0} {1} {2} {3} @'.format(xlo,ylo,xhi,yhi)
        return self.comms.send(s)

    def gbounds(self,xlo,ylo,xhi,yhi):
        s = '@[8 {0} {1} {2} {3} @'.format(xlo,ylo,xhi,yhi)
        return self.comms.send(s)

    def text(self,string):
        s = '@[9 {0} @'.format(string)
        return self.comms.send(s)

    def textsize(self,size):
        size = max(3,size)
        s = '@[A {0} @'.format(size)
        return self.comms.send(s)
        
    def textalign(self,alignment):
        aldict = {'left':0,'center':1,'right':2,'dispcenter':3}
        try:
            alcode = aldict[alignment]
        except:
            print( 'Unknown alignment name:',alignment )
            return
        s = '@[B {0} @'.format(alcode)
        return self.comms.send(s)

    def textfont(self,fontname):
        fndict = {'serif':0,'sans':1,'fixed':2}
        try:
            fncode = fndict[fontname]
        except:
            print( 'Unknown font name:',fontname )
            return
        s = '@[C {0} @'.format(fncode)
        return self.comms.send(s)

    def point(self,x,y):
        s = '@[D {0} {1} @'.format(x,y)
        return self.comms.send(s)       

    def title(self,string):
        s = '@[E {0} @'.format(string)
        return self.comms.send(s)

    def circle(self,x,y,r):
        s = '@[F {0} {1} {2}  @'.format(x,y,r)
        return self.comms.send(s)

    def square_bounds(self,yes):
        iyes = 1 if yes else 0
        s = '@[G {0} @'.format(iyes)
        return self.comms.send(s)
    
        

if __name__ == "__main__":
    gserver = GServerThread(port=51234)
    gserver.start()
    gserver.cmdq.put(GServerCommand.START)

