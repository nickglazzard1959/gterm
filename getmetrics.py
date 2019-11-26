"""Find the character cell metrics from the font image (created in Inkscape).
   Create a monochrome character texture image carefully resized from the
   blue channel of the font image. Find texture image coordinates for each
   character. Dump (by default) each cell image to its own file for use in
   building a virtual keyboard image. Two vital files are created:
   <outstem>.jsn : Character metrics & texture coordinates dictionary in JSON format.
   <outstem>.png " Font texture map in PNG monochrome format."""

import Image
import json
import optparse
import sys
import os

# Get options.
usage = "./getmetrics.py -f fontimage.png -c wxh -o fonttexturestem"
parser = optparse.OptionParser(usage=usage)
parser.add_option("-f", "--file", dest="fontimagename", default="mainfont.png")
parser.add_option("-c", "--charsize", dest="charsizestring", default="8x16")
parser.add_option("-o", "--output", dest="outstem", default="mainfonttexture")
parser.add_option("-d", "--dumpcells", dest="dumpcells", default=True)
(options,args) = parser.parse_args()

# Open the image and split in to components.
try:
    inimg = Image.open(options.fontimagename)
except:
    print 'Cannot open font image file: {0}'.format(options.fontimagename)
    sys.exit(1)
(red,green,blue,alpha) = inimg.split()

# Get the target character size.
sizewords = options.charsizestring.split('x')
if len(sizewords) != 2:
    print 'Invalid character size specification.'
try:
    cw = int(sizewords[0])
    ch = int(sizewords[1])
except:
    print 'Non numeric character size specification.'
    sys.exit(1)

# The colour data must be multiplied by the alpha or there are very odd results!
blackim = Image.new('L',blue.size)
trueblue = Image.composite(blue,blackim,alpha)
truegreen = Image.composite(green,blackim,alpha)

# Try to get metric data from the green channel.
(w,h) = truegreen.size
print 'Input image size =', w, 'X', h

# Green marks at the top mark start of each cell in x.
xpos = []
lastx = -1
for x in range(0,w):
    v = truegreen.getpixel((x,10))
    if v == 255 and (x-lastx) > 5:
        xpos.append(x)
        lastx = x

# Green marks at the left mark start of each cell in y.
ypos = []
lasty = -1
for y in range(0,h):
    v = truegreen.getpixel((10,y))
    if v == 255 and (y-lasty) > 5:
        ypos.append(y)
        lasty = y

# Green marks at the bottom mark the end of each cell in x.
xpose = []
lastx = -1
for x in range(0,w):
    v = truegreen.getpixel((x,h-10))
    if v == 255 and (x-lastx) > 5:
        xpose.append(x)
        lastx = x

# Find the average cell width.
xsize = 0.0
for i in range(0,len(xpose)):
    xsize += (xpose[i] - xpos[i])
xsize /= len(xpose)

# Green marks at the right mark the end of each cell in y.
ypose = []
lasty = -1
for y in range(0,h):
    v = truegreen.getpixel((w-10,y))
    if v == 255 and (y-lasty) > 5:
        ypose.append(y)
        lasty = y

# Find the average cell height.
ysize = 0.0
for i in range(0,len(ypose)):
    ysize += (ypose[i] - ypos[i])
ysize /= len(ypose)

# Display parameters.
print 'Target character size = ', cw, ' X ', ch
print 'Used width = ', xpose[len(xpose)-1] - xpos[0]
print 'Used height = ', ypose[len(ypose)-1] - ypos[0]
print 'Cell sizes = ', xsize, 'X', ysize
iwcell = int(xsize + 0.5)
ihcell = int(ysize + 0.5)
print 'Integer cell sizes = ',iwcell,' X ',ihcell
if options.dumpcells:
    print 'Dumping character celles as images.'

# Set margins and cut out a sensibly sized active bit.
# This was intended for use with MipMap textures with power-of-two
# requirements. But MipMapping was too fuzzy for this application.
wreq = 1024
hreq = 2048
wmargin = 50
hmargin = 0
cropblue = trueblue.crop((wmargin,hmargin,wreq+wmargin,hreq+hmargin))
cropblue.save('ZZcropblue.png')

# Get the cell locations. These are normalized texture coords.
# Put them in a dictionary with char code as the key.
charmap = {}
for xcell in range(0,16):
    for ycell in range(0,16):
        charnum = xcell+16*ycell
        topleft = (xpos[xcell]-wmargin,ypos[ycell]-hmargin)
        if options.dumpcells:
            cellimage = cropblue.crop((topleft[0],topleft[1],topleft[0]+iwcell,topleft[1]+ihcell))
            namecellimage = 'celltest_{0:03d}.png'.format(charnum)
            cellimage.save(namecellimage)
        charmap[str(charnum)]=(float(topleft[0])/wreq,float(topleft[1])/hreq)

# Output the cell size in texture map coords.
celldu = float(iwcell)/wreq
celldv = float(ihcell)/hreq
charmap['cellduv'] = (celldu,celldv)
charmap['charwidth'] = cw
charmap['charheight'] = ch
#print charmap

# Write the dictionary out in JSON format.
jsonfile = options.outstem + '.jsn'
flun = open(jsonfile,'w')
json.dump(charmap,flun,sort_keys=True)
flun.close()
print 'Wrote:', jsonfile

# Do a high quality resize of ZZcropblue.png with contrast enhancement.
# This is done by Image Magick "convert"
texim_w = int( ((float(cw)/xsize)*wreq) + 0.5 )
texim_h = int( ((float(ch)/ysize)*hreq) + 0.5 )
cmd = 'convert ZZcropblue.png -colorspace RGB -resize {0}x{1}\! -filter Mitchell  -colorspace sRGB -level 0,50% {2}.png'.format(texim_w,texim_h,options.outstem)
print cmd
stdouterr = os.popen4(cmd)[1].read()
print stdouterr
