#!/usr/bin/env python


from pynpm import NPMPackage
import subprocess
import threading
import time
import os
import requests
import sys
from zipfile import ZipFile

if __name__ == "__main__":
    path = str(os.getcwd())
    mkdir = path


    url = 'https://github.com/jishi/node-sonos-http-api/zipball/v1.0.1'
    myfile = requests.get(url, allow_redirects=True)
    open(mkdir + "/node-sonos.zip", 'wb').write(myfile.content)

    # Create a ZipFile Object and load sample.zip in it
    with ZipFile('node-sonos.zip', 'r') as zipObj:
       # Extract all the contents of zip file in current directory
       dir_name = zipObj.namelist()
       print(dir_name[0])
       zipObj.extractall()
       os.rename(dir_name[0],"node-sonos/")