"""
Assist in converting wildcard or universal imports (i.e. from thing import *)
to individual symbol imports. There are two reasons to do this:
1) A bad one: you are told you should because it is good for your soul, or something like that (it is fashionable).
2) A good one: Tools like pyflakes cannot help much if universal imports are used. They don't know if symbols are undefined or not.

Unfortunately, "fixing" this by hand is extremely tedious and error prone. There is a tool called: dewildcard 
(pip install dewildcard) written by Quentin Stafford-Fraser in 2015 which is a great start. It generates explicit imports
for *every symbol* of *every module* that is imported by a Python module.

Running pyflakes on the output of that will identify all unused symbols (a great improvement on it just saying "I don't
know if this is defined or not"). 

But (with imports like OpenGL) you can still end up with hundreds of unwanted imports to remove by hand, and pyflakes may tell
you multiple times about each symbol ...

This little program identifies which symbols are actually used using the output of pyflakes from a version of the
original Python program as modified by dewildcard.

a) Run dewildcard on your program. E.g.: dewildcard photox.py > dw-photox.py
b) Then run pyflakes on that output: E.g.: pyflakes dw-photox.py > ugh.txt
c) Then run this program. It reads ugh.txt and produces ZZZfixedimports.py

In theory (but not quite in practice), this contains per line imports of used symbols (one per line)
from each module (from which a symbol is used). You then edit the original Python program (e.g. photox.py)
and insert the appropriate parts of ZZZfixedimports.py in place of the wildcard imports. So:

d) Edit the original program (e.g. photox.py).

It isn't quite perfect, however, so we must run pyflakes on the edited program. This typically says there are
still unused imports. So:

e) Edit the original program again to remove the imports pyflakes is still complaining about.
f) Repeat until pyflakes is happy.

After doing this, any other diagnostic output from pyflakes will be valid and will not be drowned in a sea of unused
imports messages.

Still not exactly automatic, but this does make it feasible to eliminate wildcard imports for big modules without
dying first.
"""
import importlib
import sys

module_dict = {}

# Read the output of pyflakes.
pyflakes_output_file = 'ugh.txt'
with open(pyflakes_output_file,'r') as fin:
    lines = fin.readlines()

# Look for "imported but unused" and extract the module and symbol.
# For each module, build up a list of unique unused symbols.
for line in lines:
    sline = line.strip()
    if sline.endswith( 'imported but unused' ):
        words_list = sline.split()
        symbol_string = words_list[1][1:-1]
        symbol_parts = symbol_string.split('.')
        symbol = symbol_parts[-1]
        module = ""
        for symbol_part in symbol_parts[:-1]:
            module += ( symbol_part + '.' )
        module = module[:-1]
        if module not in module_dict.keys():
            module_dict[module] = []
        if symbol not in module_dict[module]:
            module_dict[module].append(symbol)
            
# For each module, get a list of ALL its symbols.
all_module_symbols_dict = {}
for module in module_dict.keys():
    if module not in all_module_symbols_dict.keys():
        all_module_symbols_dict[module] = []
        importlib.import_module(module, None)
        all_module_symbols_dict[module].append( [a for a in dir(sys.modules[module]) if not a.startswith("_")] )

# For each module, get lists of all its symbols excluding the unused symbols.
# These must be lists of used symbols.
module_used_symbols_dict = {}
for module in module_dict.keys():
    if module not in module_used_symbols_dict.keys():
        module_used_symbols_dict[module] = []
    all_module_symbols = all_module_symbols_dict[module][0]
    #print( all_module_symbols )
    for unused_symbol in module_dict[module]:
        if unused_symbol in all_module_symbols:
            #print('removing:',unused_symbol)
            all_module_symbols.remove( unused_symbol )
    module_used_symbols_dict[module] = all_module_symbols


# Create formatted import statements.
with open( "ZZZfixedimports.py", "w" ) as fout:
    for module in module_used_symbols_dict.keys():
        used_symbol_list = module_used_symbols_dict[module]
        if len(used_symbol_list) > 0:
            for symbol in used_symbol_list:
                print( 'from {0} import {1}'.format( module, symbol ), file=fout )
            print(' ', file=fout)
