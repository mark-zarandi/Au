#!/usr/bin/python
from subprocess import Popen
import sys
import subprocess


clear_screen_seq = subprocess.check_output('clear')
filename = sys.argv[1]
while True:
    #print("\nStarting " + filename)
    p = Popen("python3 " + filename, shell=True)
    p.wait()
