#!/usr/bin/env python3
import struct
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('inlogfile',help='Input ctelnet log file to convert to raw Tek4010 codes.')
parser.add_argument('outpltfile',help='Output Tek4010 codes file.')
args = parser.parse_args()

with open(args.inlogfile,'r') as fin:
    lines = fin.readlines()

with open(args.outpltfile,'wb') as fout:
    lineno = 0
    for line in lines:
        lineno += 1
        if line[:2] == 'I ':
            hexpart = line[11:13]
            try:
                hexint = int(hexpart,16)
            except:
                print('ERROR, line number:',lineno,' line:',line[1:3])
                sys.exit(2)
            fout.write( struct.pack('B',(hexint&0xff)) )
