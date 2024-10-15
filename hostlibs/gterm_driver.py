#!/usr/bin/env python
import sys
import random

class GtermGraphics(object):
    """
    Output GTerm compatible graphics commands.
    Fixed mode is for DIMFILM, basically. The default mode implements something like
    a very simple standalone graphics library rather than a totally dumb device.
    """

    def __init__(self,lun=sys.stdout,fixedmode=False):
        self.lun = lun
        self.fixedmode = fixedmode

    def unavailable(self, msg):
        print('Function: {0}() is unavailable in fixed mode.'.format(msg))

    def clamp(self,v,lo,hi):
        return max(lo,min(v,hi))

    def clear(self):
        """
        Empty the graphics display list. Clear the screen, in effect.
        """
        if self.fixedmode:
            self.lun.write('\033[0z')
        else:
            self.lun.write('@[0@')

    def colour(self,r,g,b):
        """
        Set the drawing colour.
        """
        if self.fixedmode:
            ir = self.clamp(int(999.9*r),0,999)
            ig = self.clamp(int(999.9*g),0,999)
            ib = self.clamp(int(999.9*b),0,999)
            s = '\033[1{0:03d}{1:03d}{2:03d}z'.format(ir,ig,ib)
        else:
            ir = self.clamp(r,0.0,1.0)
            ig = self.clamp(g,0.0,1.0)
            ib = self.clamp(b,0.0,1.0)
            s = '@[1 {0:.3f} {1:.3f} {2:.3f} @'.format(ir,ig,ib)
        self.lun.write(s)

    def erase(self):
        """
        Fill the display with the drawing colour.
        """
        if self.fixedmode:
            self.lun.write('\033[2z')
        else:
            self.lun.write('@[2@')

    def pen(self,x,y,z,rel=False):
        if z > 0:
            c = 'I' if rel else 4
        else:
            c = 'H' if rel else 3
        if self.fixedmode:
            if rel:
                self.unavailable('relative move or draw')
                return
            else:
                ix = self.clamp(int(9999.9*x),0,9999)
                iy = self.clamp(int(9999.9*y),0,9999)
                s = '\033[{0:1d}{1:04d}{2:04d}z'.format(c,ix,iy)
        else:
            s = '@[{0} {1} {2} @'.format(c,x,y)
        self.lun.write(s)

    def move(self,x,y):
        """
        Move to user coordinates (x,y). In fixed mode, the user coordinates
        are fixed at (0,0) to (1,1) corresponsding to the bottom laft and top right.
        In "altmode", these are set by bounds() or gbounds().
        """
        self.pen(x,y,0)

    def draw(self,x,y):
        """
        Draw to user coordinates (x,y).
        """
        self.pen(x,y,1)

    def moverel(self,dx,dy):
        """
        Relative move from current position by (dx,dy).
        """
        if self.fixedmode:
            self.unavailable('moverel')
        else:
            self.pen(dx,dy,0,rel=True)

    def drawrel(self,dx,dy):
        """
        Relative draw from current position by (dx,dy).
        """
        if self.fixedmode:
            self.unavailable('drawrel')
        else:
            self.pen(dx,dy,1,rel=True)
        
    def flush(self):
        """
        Ensure the contents of the display list are drawn.
        """
        if self.fixedmode:
            self.lun.write('\033[5z')
        else:
            self.lun.write('@[5@')        

    def width(self,w):
        """
        Set the line drawing width in pixels (as far as possible).
        """
        if self.fixedmode:
            iw = self.clamp(int(99.9*w),0,999)
            s = '\033[6{0:03d}z'.format(iw)
        else:
            iw = self.clamp(w,0.0,9.0)
            s = '@[6 {0} @'.format(iw)
        self.lun.write(s)

    def bounds(self,xlo,ylo,xhi,yhi):
        """
        Set up the user coordinate system. Bottom left of the display is at (xlo,ylo)
        and top right is at (xhi,yhi). If square_mode() has been previously issued, the
        *X* bounds will be adjusted so that something that is sqaure in user coords appears
        square in the display.
        """
        if self.fixedmode:
            self.unavailable('bounds')
        else:
            s = '@[7 {0} {1} {2} {3} @'.format(xlo,ylo,xhi,yhi)
            self.lun.write(s)

    def gbounds(self,xlo,ylo,xhi,yhi):
        """
        Set the data range for simple graph drawing. The values specified are internally modified
        based on "tick values" to get a generally pleasing range and starting value. If square_mode()
        has previously been used, the *X* range is adjusted so that the tick intervals are the same on both
        axes and the X range is *centered on* the supplied X range.
        """
        if self.fixedmode:
            self.unavailable('gbounds')
        else:
            s = '@[8 {0} {1} {2} {3} @'.format(xlo,ylo,xhi,yhi)
            self.lun.write(s)

    def text(self,string):
        """
        Output text at the last move() location.
        """
        if self.fixedmode:
            self.unavailable('text')
        else:
            s = '@[9 {0} @'.format(string)
            self.lun.write(s)

    def textsize(self,size):
        """
        Set the size of the text in somewhat arbitrary units. 14 is arguably normal size text.
        """
        if self.fixedmode:
            self.unavailable('textsize')
        else:
            size = max(3,size)
            s = '@[A {0} @'.format(size)
            self.lun.write(s)
        
    def textalign(self,alignment):
        """
        Set how subsequent text() is aligned with the move() immediately preceding it.
        alignment 'left' has the text() start there, 'right' has it end there and
        center has it be centered there. 'dispcenter' has it centered in X on the display.
        """
        if self.fixedmode:
            self.unavailable('textalign')
        else:
            aldict = {'left':0,'center':1,'right':2,'dispcenter':3}
            try:
                alcode = aldict[alignment]
            except:
                print('Unknown alignment name:',alignment)
                return
            s = '@[B {0} @'.format(alcode)
            self.lun.write(s)

    def textfont(self,fontname):
        """
        Choose a font type (very roughly). Only three choices, as this is not intended
        to be a typesetting solution! 'serif', 'sans' and 'fixed'.
        """
        if self.fixedmode:
            self.unavailable('textfont')
        else:        
            fndict = {'serif':0,'sans':1,'fixed':2}
            try:
                fncode = fndict[fontname]
            except:
                print('Unknown font name:',fontname)
                return
            s = '@[C {0} @'.format(fncode)
            self.lun.write(s)

    def point(self,x,y):
        """
        Draw a point at user coordinates (x,y).
        """
        if self.fixedmode:
            self.unavailable('point')
        else:         
            s = '@[D {0} {1} @'.format(x,y)
            self.lun.write(s)       

    def title(self,string):
        """
        Draw a graph title in a fixed size and font centered on the display.
        """
        if self.fixedmode:
            self.unavailable('title')
        else:     
            s = '@[E {0} @'.format(string)
            self.lun.write(s)

    def circle(self,x,y,r):
        """
        Draw a circle, center user coords (x,y), radius user X units r. This is always a circle, regardless of
        the bounds set.
        """
        if self.fixedmode:
            self.unavailable('circle')
        else:         
            s = '@[F {0} {1} {2}  @'.format(x,y,r)
            self.lun.write(s)

    def square_bounds(self,yes):
        """
        Modify subsequent bounds() and gbounds() calls so that if a square is drawn in user coordinates
        it appears square on the display.
        """
        if self.fixedmode:
            self.unavailable('square_bounds')
        else:        
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

    gt = GtermGraphics(sys.stdout, fixedmode=False)
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
        gt.text('Hello all')
        gt.move(0.5,1.7)
        gt.text('Hello again...')
        gt.textsize(25)
        gt.textalign('center')
        gt.move(0.5,1.9)
        gt.text('Hello BIG people.')
        gt.textsize(14)
        gt.textalign('right')
        gt.textfont('sans')
        gt.move(0.5,2.1)
        gt.text('Hello smaller people on the right')
        gt.textalign('dispcenter')
        gt.textsize(20)
        gt.textfont('fixed')
        gt.move(0.5,2.3)
        gt.text('Hello people in the middle')
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
