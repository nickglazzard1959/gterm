""" Make a virtual keyboard image from a JSON format virtual keyboard
    definition file. The definition file must be created by hand."""

from PIL import Image
from PIL import ImageDraw
import json
import optparse
import sys
import os

# Get options.
usage = "./makevkb.py -i definitions.jsn -o vkbimage.png [-c cellimagestem]"
parser = optparse.OptionParser(usage=usage)
parser.add_option("-i", "--input", dest="definitions", default="definitions.jsn")
parser.add_option("-o", "--output", dest="outimage", default="vkbimage.png")
parser.add_option("-c", "--cellstem", dest="cellstem", default="celltest_")
(options,args) = parser.parse_args()

# Open the definitions JSON file.
# Read and parse the contents.
try:
    flun = open(options.definitions,'r')
    input_keydata = json.load(flun)
    flun.close()
    vkb_keymap = {}
    vkblayoutdict = {}
    inputkeyposmap = input_keydata['keyposmap']
    for k in inputkeyposmap:
        try:
            ikey = int(k)
            vkb_keymap[ikey] = inputkeyposmap[k]
        except:
            pass
        vkb_keycols = input_keydata['keycols']
        vkb_keyrows = input_keydata['keyrows']
        vkb_keyxdelta = input_keydata['keyxdelta']
        vkb_keyydelta = input_keydata['keyydelta']
except:
    print('**** Failed to read virtual keyboard definition file:', options.definitions, 'Giving up!')
    sys.exit(1)

# Open an output image.
image_width = vkb_keycols * vkb_keyxdelta
image_height = vkb_keyrows * vkb_keyydelta
print('Result image size will be:',image_width,'X',image_height)
nkeys = vkb_keycols * vkb_keyrows
if nkeys != len(vkb_keymap):
    print('**** Number of keys:',nkeys,'inconsistent with keymap length.',len(vkb_keymap),'Giving up!')
outimage = Image.new('L',(image_width,image_height),230)

# For every key, composite the right key image in to the correct
# key position.
for ikey in range(0,len(vkb_keymap)):
    xloc = ikey % vkb_keycols
    yloc = ikey // vkb_keycols
    (charcode,keydesc) = vkb_keymap[ikey]
    cellimagename = options.cellstem + '{0:03d}.png'.format(charcode)
    print(xloc, yloc, charcode, cellimagename)
    inimage = Image.open(cellimagename)
    insize = inimage.size
    inasprat = float(insize[0])/float(insize[1])
    ymargin = 5
    margin_keyydelta = vkb_keyydelta - (2*ymargin)
    pastesize = (int(margin_keyydelta*inasprat),margin_keyydelta)
    sizedinimage = inimage.resize(pastesize,Image.LANCZOS)
    colsizedinimage = Image.eval(sizedinimage,lambda p:min(255-p,230))
    xoffset = ( vkb_keyxdelta - pastesize[0] ) // 2 + 2
    yoffset = 2
    outimage.paste(colsizedinimage,(xloc*vkb_keyxdelta+xoffset,yloc*vkb_keyydelta+ymargin+yoffset))

# Draw the key dividers.
draw = ImageDraw.Draw(outimage)
for xpos in range(0,image_width,vkb_keyxdelta):
    draw.line([(xpos,0),(xpos,image_height-1)])
    draw.line([(xpos+1,0),(xpos+1,image_height-1)])
draw.line([(image_width-2,0),(image_width-2,image_height-1)])
draw.line([(image_width-1,0),(image_width-1,image_height-1)])
for ypos in range(0,image_height,vkb_keyydelta):
    draw.line([(0,ypos),(image_width-1,ypos)])
    draw.line([(0,ypos+1),(image_width-1,ypos+1)])
draw.line([(0,image_height-2),(image_width-1,image_height-2)])
draw.line([(0,image_height-1),(image_width-1,image_height-1)])
outimage.save(options.outimage)
print("Wrote:",options.outimage)
