import sys, traceback, signal
import threading
import os

def dumpstacks(signal, frame):
  id2name = dict((th.ident, th.name) for th in threading.enumerate())
  for threadId, stack in sys._current_frames().items():
    print(id2name[threadId])
    traceback.print_stack(f=stack)

signal.signal(signal.SIGQUIT, dumpstacks)

os.killpg(os.getpgid(0), signal.SIGQUIT)
