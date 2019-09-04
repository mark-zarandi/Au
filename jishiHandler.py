#!/usr/bin/env python


from pynpm import NPMPackage
import subprocess
import threading
import time
import os
import requests
from zipfile import ZipFile
def jishiInstaller():

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
    print('unzipped')


class jishiReader:

    def __init__(self, json_loc):
        not_here = False
        if os.path.exists(json_loc) != True:
            jishiInstaller()
            not_here = True

        
        if not_here:
            self.pkg = NPMPackage(json_loc)
            self.pkg.install('--production',wait=False)
            time.sleep(15)

            self.pkg = NPMPackage(json_loc) 
        else:
            self.pkg = NPMPackage(json_loc)   
        self.spin_success = True
        self.log_npm = []
        self.start_thread()
        #returns Popen MZ: RUN THIS IN A THREAD
    def spin_npm(self):
        try:
            self.proc = self.pkg.run_script('start',wait=False)
            while True:
                line = self.proc.stdout.readline()
                if not line:
                    break
                self.log_npm.append(line) 
        except:
            self.spin_success = False

    def start_thread(self):
        t = threading.Thread(name="jishi_thread",target=self.spin_npm)
        print("made it")
        t.start()
    def get_log(self):
        return self.spin_success


if __name__ == "__main__":	
    #location of node sonos package.

    load_npm = jishiReader('./node-sonos/package.json')
    time.sleep(5)
    print(load_npm.get_log())
