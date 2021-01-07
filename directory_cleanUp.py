#!/usr/bin/env python3

import os
import re

def rename_files(path):
    files = {}
    otherpath = os.path.join(path,"Other")
    if not os.path.exists(otherpath):
        os.mkdir(otherpath)
    with os.scandir(path) as entries:
        for entry in entries:
            if "(j)" not in entry.name.lower():
                fname = entry.name
                newname = re.sub('\([,a-zA-Z!@#$%^&*\[\]]*\)','',fname).lower().replace(' .','.').title().replace("(","").replace(")","")
                firstdigit = True
                finalname = ""
                for c in newname:
                    if c.isdigit():
                        if firstdigit:
                            finalname += " " + c
                            firstdigit = False
                        else:
                            finalname += c
                            
                    else:
                        finalname += c
                        firstdigit = True
                if ' The.' in fname:
                    finalname = 'The ' + finalname.replace(' The.','')
                finalname = finalname.replace("  "," ").strip()
                if finalname != fname:
                    if not os.path.exists(path + finalname):
                        print("renaming: " + fname + " -> " + finalname)
                        os.rename(path + fname,path + finalname)
                    else:
                        print('problem: ' + fname +' ->  ' + finalname)
                else:
                    print('done: ' + fname)
            else:
                if not os.path.exists(os.path.join(otherpath,entry.name)):
                    print('moving: ' + os.path.join(path,entry.name + "-> " + os.path.join(otherpath,entry.name)))
                    os.rename(os.path.join(path,entry.name), os.path.join(otherpath,entry.name))
                else:
                    print('problem-other: ' + entry.name)

def main():
    rename_files("/home/pete/Downloads/RomsCopy/test/")

if __name__ == "__main__":
    main()