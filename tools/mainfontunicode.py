# Associate GTerm internal 8 bit character numbers with
# Unicode code points for display and printing log files.
# This tries to match ISO-IEC/JTC1/SC22 N 3067 which is
# supposed to be the international standard mapping APL
# symbols to Unicode code points. I believe the APL 385
# Unicode True Type font implements this. Make any changes
# here, then run this file to generate mainfontunicode.jsn
# for use by GTerm.

import json

unicode_map = {
    0x00:'\\u2400', # ANSI/ASCII: control characters
    0x01:'\\u2401',
    0x02:'\\u2402',
    0x03:'\\u2403',
    0x04:'\\u2404',
    0x05:'\\u2405',
    0x06:'\\u2406',
    0x07:'\\u2407',
    0x08:'\\u2408',
    0x09:'\\u2409',
    0x0a:'\\u240a',
    0x0b:'\\u240b',
    0x0c:'\\u240c',
    0x0d:'\\u240d',
    0x0e:'\\u240e',
    0x0f:'\\u240f',
    0x10:'\\u2410',
    0x11:'\\u2411',
    0x12:'\\u2412',
    0x13:'\\u2413',
    0x14:'\\u2414',
    0x15:'\\u2415',
    0x16:'\\u2416',
    0x17:'\\u2417',
    0x18:'\\u2418',
    0x19:'\\u2419',
    0x1a:'\\u241a',
    0x1b:'\\u241b',
    0x1c:'\\u241c',
    0x1d:'\\u241d',
    0x1e:'\\u241e',
    0x1f:'\\u241f',
    0x20:'\\u0020', # space
    0x21:'\\u0021', # punctuation
    0x22:'\\u0022',
    0x23:'\\u0023',
    0x24:'\\u0024',
    0x25:'\\u0025',
    0x26:'\\u0026',
    0x27:'\\u0027',
    0x28:'\\u0028',
    0x29:'\\u0029',
    0x2a:'\\u002a',
    0x2b:'\\u002b',
    0x2c:'\\u002c',
    0x2d:'\\u002d',
    0x2e:'\\u002e',
    0x2f:'\\u002f',
    0x30:'\\u0030', # digits
    0x31:'\\u0031',
    0x32:'\\u0032',
    0x33:'\\u0033',
    0x34:'\\u0034',
    0x35:'\\u0035',
    0x36:'\\u0036',
    0x37:'\\u0037',
    0x38:'\\u0038',
    0x39:'\\u0039',
    0x3a:'\\u003a', # punctuation, etc.
    0x3b:'\\u003b',
    0x3c:'\\u003c',
    0x3d:'\\u003d',
    0x3e:'\\u003e',
    0x3f:'\\u003f',
    0x40:'\\u0040',
    0x41:'\\u0041', # Capital letters
    0x42:'\\u0042',
    0x43:'\\u0043',
    0x44:'\\u0044',
    0x45:'\\u0045',
    0x46:'\\u0046',
    0x47:'\\u0047',
    0x48:'\\u0048',
    0x49:'\\u0049',
    0x4a:'\\u004a',
    0x4b:'\\u004b',
    0x4c:'\\u004c',
    0x4d:'\\u004d',
    0x4e:'\\u004e',
    0x4f:'\\u004f',
    0x50:'\\u0050',
    0x51:'\\u0051',
    0x52:'\\u0052',
    0x53:'\\u0053',
    0x54:'\\u0054',
    0x55:'\\u0055',
    0x56:'\\u0056',
    0x57:'\\u0057',
    0x58:'\\u0058',
    0x59:'\\u0059',
    0x5a:'\\u005a', # punctuation, etc.
    0x5b:'\\u005b',
    0x5c:'\\u005c',
    0x5d:'\\u005d',
    0x5e:'\\u005e',
    0x5f:'\\u005f',
    0x60:'\\u0060',
    0x61:'\\u0061', # lower case letters
    0x62:'\\u0062',
    0x63:'\\u0063',
    0x64:'\\u0064',
    0x65:'\\u0065',
    0x66:'\\u0066',
    0x67:'\\u0067',
    0x68:'\\u0068',
    0x69:'\\u0069',
    0x6a:'\\u006a',
    0x6b:'\\u006b',
    0x6c:'\\u006c',
    0x6d:'\\u006d',
    0x6e:'\\u006e',
    0x6f:'\\u006f',
    0x70:'\\u0070',
    0x71:'\\u0071',
    0x72:'\\u0072',
    0x73:'\\u0073',
    0x74:'\\u0074',
    0x75:'\\u0075',
    0x76:'\\u0076',
    0x77:'\\u0077',
    0x78:'\\u0078',
    0x79:'\\u0079',
    0x7a:'\\u007a',
    0x7b:'\\u007b', # braces etc.
    0x7c:'\\u007c',
    0x7d:'\\u007d',
    0x7e:'\\u007e',
    0x7f:'\\u007f', # del / 7f
    0x80:'\\u226a', # MATHS: v much less than
    0x81:'\\u226b', # v much gt than
    0x82:'\\u2229', # intersection
    0x83:'\\u222a', # union
    0x84:'\\u220f', # continued product
    0x85:'\\u2282', # subset of
    0x86:'\\u2283', # superset of
    0x87:'\\u221a', # sqrt
    0x88:'\\u21d0', # left double arrow
    0x89:'\\u21d2', # right double arrow
    0x8a:'\\u2103', # SUNDRY: degrees C
    0x8b:'\\u00a7', # section
    0x8c:'\\u00b6', # para
    0x8d:'\\u00a5', # CURRENCY: yen
    0x8e:'\\u0e3f', # baht
    0x8f:'\\u00a2', # cent
    0x90:'\\u20ac', # euro
    0x91:'\\u00b0', # degree
    0x92:'\\u00f7', # division
    0x93:'\\u00a3', # pound
    0x94:'\\u223c', # not (was 00ac ASCII tilde but APL385 doesn't like that)
    0x95:'\\u233d', # APL: apl rotate
    0x96:'\\u22a5', # apl base
    0x97:'\\u22a4', # apl represent
    0x98:'\\u234e', # apl execute
    0x99:'\\u2355', # apl format
    0x9a:'\\u2349', # apl transpose
    0x9b:'\\u2192', # apl branch
    0x9c:'\\u25af', # apl quad (was 2395)
    0x9d:'\\u235e', # apl quote quad
    0x9e:'\\u2296', # apl 1st coord rotate
    0x9f:'\\u236b', # apl locked function
    0xa0:'\\u2190', # apl is
    0xa1:'\\u235d', # apl comment
    0xa2:'\\u25ae', # apl bad char (black rectangle)
    0xa3:'\\u2359', # apl underlined delta
    0xa4:'\\u2361', # apl out
    0xa5:'\\u2445', # bow tie ?
    0xa6:'\\u00a8', # diaeresis
    0xa7:'\\u2200', # for all
    0xa8:'\\u2203', # there exists
    0xa9:'\\u2202', # partial differential
    0xaa:'\\u2245', # approximately equal
    0xab:'\\u2261', # identical to
    0xac:'\\u221e', # infinity
    0xad:'\\u223f', # sine
    0xae:'\\u00af', # apl negative (was 207b)
    0xaf:'\\u2234', # therefore
    0xb0:'\\u2193', # apl drop
    0xb1:'\\u2191', # apl take
    0xb2:'\\u233f', # apl 1st c compress
    0xb3:'\\u2340', # apl 1st c expand
    0xb4:'\\u2207', # apl del (nabla)
    0xb5:'\\u2352', # apl grade down
    0xb6:'\\u234b', # apl grade up
    0xb7:'\\u220a', # apl membership (was 22ff)
    0xb8:'\\u2339', # apl matrix divide
    0xb9:'\\u2373', # apl index
    0xba:'\\u236a', # apl 1st c join
    0xbb:'\\u2374', # apl reshape
    0xbc:'\\u2371', # apl down caret tilde
    0xbd:'\\u2372', # apl up caret tilde
    0xbe:'\\u2228', # logical or (was 22c1)
    0xbf:'\\u2227', # logical and (was 22c0)
    0xc0:'\\u2265', # >=
    0xc1:'\\u2264', # <=
    0xc2:'\\u2260', # not =
    0xc3:'\\u25cb', # white circle
    0xc4:'\\u25cf', # black circle
    0xc5:'\\u230b', # floor
    0xc6:'\\u2308', # ceiling
    0xc7:'\\u002b', # plus
    0xc8:'\\u00d7', # multiply (was 2a09)
    0xc9:'\\u0393', # GREEK: Gamma
    0xca:'\\u0394', # Delta
    0xcb:'\\u0398', # Theta
    0xcc:'\\u039b', # Lambda
    0xcd:'\\u039e', # Xi
    0xce:'\\u03a0', # Pi
    0xcf:'\\u03a3', # Sigma
    0xd0:'\\u03a6', # Phi
    0xd1:'\\u03a8', # Psi
    0xd2:'\\u03a9', # Omega
    0xd3:'\\u03b1', # alpha
    0xd4:'\\u03b2', # beta
    0xd5:'\\u03b3', # gamma
    0xd6:'\\u03b4', # delta
    0xd7:'\\u03b5', # epsilon
    0xd8:'\\u03b6', # zeta
    0xd9:'\\u03b7', # eta
    0xda:'\\u03b8', # theta
    0xdb:'\\u03b9', # iota
    0xdc:'\\u03ba', # kappa
    0xdd:'\\u03bb', # lambda
    0xde:'\\u03bc', # mu
    0xdf:'\\u03bd', # nu
    0xe0:'\\u03be', # xi
    0xe1:'\\u03bf', # omicron
    0xe2:'\\u03c0', # pi
    0xe3:'\\u03c1', # rho
    0xe4:'\\u03c3', # sigma
    0xe5:'\\u03c4', # tau
    0xe6:'\\u03c5', # upsilon
    0xe7:'\\u03c6', # phi
    0xe8:'\\u03c7', # chi
    0xe9:'\\u03c8', # psi
    0xea:'\\u03c9', # omega
    0xeb:'\\u00df', # GERMAN/NORDIC: german sharp s s-set
    0xec:'\\u00e4', # a umlaut
    0xed:'\\u00e5', # a ring
    0xee:'\\u00eb', # e umlaut
    0xef:'\\u00fc', # u umlaut
    0xf0:'\\u00c6', # AE
    0xf1:'\\u00e6', # ae
    0xf2:'\\u00d0', # Eth -D
    0xf3:'\\u00f0', # eth -d
    0xf4:'\\u00de', # Thorn
    0xf5:'\\u00fe', # thorn
    0xf6:'\\u00d6', # O umlaut
    0xf7:'\\u00f6', # o umlaut
    0xf8:'\\u00c4', # A umlaut
    0xf9:'\\u00cb', # E umlaut
    0xfa:'\\u00cf', # I umlaut
    0xfb:'\\u00dc', # U umlaut
    0xfc:'\\u0178', # Y umlaut
    0xfd:'\\u00ff', # y umlaut
    0xfe:'\\u235f', # APL logarithm (circle/star) (was 272a)
    0xff:'\\u2218', # APL outer product (small circle) (was 26ac)
}
# Write the dictionary out in JSON format.
jsonfile = 'mainfontunicode' + '.jsn'
flun = open(jsonfile,'w')
json.dump(unicode_map,flun,sort_keys=True)
flun.close()
print('Wrote:', jsonfile)
