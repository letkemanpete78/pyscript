#!/usr/bin/env python3

import os
import re
import glob


def handle_dups(path,filenames):
    filenames.sort(key=trim_filename)
    duppath = os.path.join(path,"dups")
    if not os.path.exists(duppath):
        os.mkdir(duppath)
    for filename in filenames:
        file_subset = glob.glob(os.path.join(path, filename) + '*')
        if len(file_subset) > 1:
            dupfiles = []
            for name in file_subset:
                dupfiles.append({'name':os.path.basename(name), 'size':os.stat(name).st_size})
            dupfiles = sorted(dupfiles, key=lambda x: x['size'],reverse=True)[1:]
            for f in dupfiles:
                dst = os.path.join(path,duppath,f['name'])
                src = os.path.join(path,f['name'])
                os.rename(src,dst)
                print('moving dup: ',src,'->',dst)

def trim_filename(name):
    if len(name) > 6:
        name = name[:-8]
    elif len(name) > 3:
        name = name[:-4]
    return name

def rename_files(path):
    filenames = []
    otherpath = os.path.join(path,"Other")
    if not os.path.exists(otherpath):
        os.mkdir(otherpath)
    with os.scandir(path) as entries:
        for entry in entries:
            if not os.path.isdir(os.path.join(path,entry.name)):
                if "(j)" not in entry.name.lower():
                    fname = entry.name
                    newname = re.sub('\([a-zA-Z!@#$%^&*\[\]]*\)','',fname).lower().replace(' .','.').title().replace('(','').replace(')','').replace(',','.').replace('-',' ').replace('_',' ')
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
                            filenames.append(trim_filename(finalname).replace('.',''))
                        else:
                            print('problem: ' + fname +' ->  ' + finalname)
                    else:
                        print('done: ' + fname)
                        filenames.append(trim_filename(fname).replace('.',''))
                else:
                    if not os.path.exists(os.path.join(otherpath,entry.name)):
                        print('moving: ' + os.path.join(path,entry.name + "-> " + os.path.join(otherpath,entry.name)))
                        os.rename(os.path.join(path,entry.name), os.path.join(otherpath,entry.name))
                    else:
                        print('problem-other: ' + entry.name)
    return list(set(filenames))

def main():
    path = "/home/pete/Downloads/RomsCopy/test/"
    filenames = rename_files(path)
    handle_dups(path,filenames)

if __name__ == "__main__":
    main()