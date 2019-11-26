#!/usr/bin/env python
import sys
import random

class GtGraf(object):
    """Output GTerm compatible graphics."""

    def __init__(self,lun):
        self.lun = lun

    def clamp(self,v,lo,hi):
        return max(lo,min(v,hi))

    def clear(self):
        self.lun.write('@[0Z')

    def colour(self,r,g,b):
        ir = self.clamp(int(999.9*r),0,999)
        ig = self.clamp(int(999.9*g),0,999)
        ib = self.clamp(int(999.9*b),0,999)
        s = '@[1 {0:3d} {1:3d} {2:3d} Z'.format(ir,ig,ib)
        self.lun.write(s)

    def erase(self):
        self.lun.write('@[2Z')

    def pen(self,x,y,z):
        if z > 0:
            c = 4
        else:
            c = 3
        ix = self.clamp(int(9999.9*x),0,9999)
        iy = self.clamp(int(9999.9*y),0,9999)
        s = '@[{0:1d} {1: 4d} {2:4d} Z'.format(c,ix,iy)
        self.lun.write(s)

    def move(self,x,y):
        self.pen(x,y,0)

    def draw(self,x,y):
        self.pen(x,y,1)

    def width(self,w):
        iw = self.clamp(int(99.9*w),0,999)
        s = '@[6 {0:3d} Z'.format(iw)
        self.lun.write(s)

    def flush(self):
        self.lun.write('@[5Z')

def draw_random_line(gt):
    xs = random.random()
    ys = random.random()
    xe = random.random()
    ye = random.random()
    r = random.random()
    g = random.random()
    b = random.random()
    w = 10.0*random.random()
    gt.colour(r,g,b)
    gt.width(w)
    gt.move(xs,ys)
    gt.draw(xe,ye)

gt = GtGraf(sys.stdout)
gt.clear()
gt.colour(0,0.5,1.0)
gt.erase()
gt.colour(0,0,0)
gt.move(0.1,0.1)
gt.draw(0.9,0.7)
gt.flush()

nrand = 100
for i in range(0,nrand):
    draw_random_line(gt)
