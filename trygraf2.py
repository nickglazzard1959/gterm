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
        self.lun.write('@[0@')

    def colour(self,r,g,b):
        ir = self.clamp(r,0.0,1.0)
        ig = self.clamp(g,0.0,1.0)
        ib = self.clamp(b,0.0,1.0)
        s = '@[1 {0:.3f} {1:.3f} {2:.3f} @'.format(ir,ig,ib)
        self.lun.write(s)

    def erase(self):
        self.lun.write('@[2@')

    def pen(self,x,y,z):
        if z > 0:
            c = 4
        else:
            c = 3
        s = '@[{0} {1} {2} @'.format(c,x,y)
        self.lun.write(s)

    def move(self,x,y):
        self.pen(x,y,0)

    def draw(self,x,y):
        self.pen(x,y,1)

    def flush(self):
        self.lun.write('@[5@')        

    def width(self,w):
        iw = self.clamp(w,0.0,9.0)
        s = '@[6 {0} @'.format(iw)
        self.lun.write(s)

    def bounds(self,xlo,ylo,xhi,yhi):
        s = '@[7 {0} {1} {2} {3} @'.format(xlo,ylo,xhi,yhi)
        self.lun.write(s)

    def gbounds(self,xlo,ylo,xhi,yhi):
        s = '@[8 {0} {1} {2} {3} @'.format(xlo,ylo,xhi,yhi)
        self.lun.write(s)

    def text(self,string):
        s = '@[9 {0} @'.format(string)
        self.lun.write(s)

    def textsize(self,size):
        size = max(3,size)
        s = '@[A {0} @'.format(size)
        self.lun.write(s)
        
    def textalign(self,alignment):
        aldict = {'left':0,'center':1,'right':2,'dispcenter':3}
        try:
            alcode = aldict[alignment]
        except:
            print 'Unknown alignment name:',alignment
            return
        s = '@[B {0} @'.format(alcode)
        self.lun.write(s)

    def textfont(self,fontname):
        fndict = {'serif':0,'sans':1,'fixed':2}
        try:
            fncode = fndict[fontname]
        except:
            print 'Unknown font name:',fontname
            return
        s = '@[C {0} @'.format(fncode)
        self.lun.write(s)

    def point(self,x,y):
        s = '@[D {0} {1} @'.format(x,y)
        self.lun.write(s)       

    def title(self,string):
        s = '@[E {0} @'.format(string)
        self.lun.write(s)

    def circle(self,x,y,r):
        s = '@[F {0} {1} {2}  @'.format(x,y,r)
        self.lun.write(s)

    def square_bounds(self,yes):
        iyes = 1 if yes else 0
        s = '@[G {0} @'.format(iyes)
        self.lun.write(s)

if __name__ == "__main__":

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

    def draw_random_point(gt):
        xs = 2*random.random()
        ys = 2*random.random()
        r = random.random()
        g = random.random()
        b = random.random()
        gt.colour(r,g,b)
        gt.point(xs,ys)

    def draw_random_circle(gt):
        xs = 2*random.random()
        ys = 2*random.random()
        rad = 0.25 * random.random()
        r = random.random()
        g = random.random()
        b = random.random()
        gt.colour(r,g,b)
        gt.circle(xs,ys,rad)        

    gt = GtGraf(sys.stdout)
    gt.clear()
    # gt.colour(0,0.5,1.0)
    gt.colour(1.0,1.0,1.0)
    gt.erase()
    gt.square_bounds(True)
    gt.gbounds(-0.5,-0.5,2.0,2.5)
    #gt.gbounds(-1000,-500,2000,2500)
    gt.colour(0,0,0)
    gt.move(0.1,0.1)
    gt.draw(0.9,0.7)
    gt.flush()

    if False:
        gt.move(0.5,1.5)
        gt.textsize(14)
        gt.textalign('left')
        gt.text('Hello girls')
        gt.move(0.5,1.7)
        gt.text('Hello again...')
        gt.textsize(25)
        gt.textalign('center')
        gt.move(0.5,1.9)
        gt.text('Hello BIG girls.')
        gt.textsize(14)
        gt.textalign('right')
        gt.textfont('sans')
        gt.move(0.5,2.1)
        gt.text('Hello smaller girls on the right')
        gt.textalign('dispcenter')
        gt.textsize(20)
        gt.textfont('fixed')
        gt.move(0.5,2.3)
        gt.text('Hello girls in the middle')
        gt.flush()

    gt.colour(0,0,0)
    gt.title('We Tried')

    nrand = 100
    for i in range(0,nrand):
        draw_random_line(gt)

    gt.width(1)
    for i in range(0,nrand):
        draw_random_point(gt)

    for i in range(0,nrand):
        draw_random_circle(gt)
