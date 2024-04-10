#!/usr/bin/env python
import subprocess
hashstr = subprocess.check_output(['git','rev-parse','HEAD'])
descstr = subprocess.check_output(['git','describe','master'])
flun = open('./githashvalue.py','w')
flun.write('_current_git_desc="{0}"\n'.format(descstr.strip()))
flun.write('_current_git_hash="{0}"\n'.format(hashstr.strip()))
flun.close()
