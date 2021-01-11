#!/usr/bin/env python3

import os
import re
import glob


def handle_dups(path,filenames):
    filenames.sort(key=trim_filename)
    duppath = os.path.join(path,"dups")
    with open('dups.txt', 'w') as duplog:
        if not os.path.exists(duppath):
            os.mkdir(duppath)
            duplog.write('Created directory: ' + duppath + "\n")
        for filename in filenames:
            file_subset = None
            if filename == '':
                continue
            f = replace('the ','????',filename.strip())
            f = replace(' the','????',f)
            f = f.replace('.','?').replace(' ','?') + '?*'
            while ('?????' in f):
                f = f.replace('?????','????')
            file_subset = glob.glob(os.path.join(path, f))
            if len(file_subset) > 1:
                dupfiles = []
                for name in file_subset:
                    dupfiles.append({'name':os.path.basename(name), 'size':os.stat(name).st_size})
                dupfiles = sorted(dupfiles, key=lambda x: x['size'],reverse=True)[1:]
                for f in dupfiles[1:]:
                    dst = os.path.join(path,duppath,f['name'])
                    src = os.path.join(path,f['name'])
                    if not os.path.isdir(dst) and not os.path.isdir(src):
                        os.rename(src,dst)
                        duplog.write('moving dup: ' + src + ' -> ' + dst + "\n")

def replace(old, new, str, caseinsentive = False):
    if caseinsentive:
        return str.replace(old, new)
    else:
        return re.sub(re.escape(old), new, str, flags=re.IGNORECASE)

def trim_filename(in_name):
    name = in_name
    if len(name) > 6:
        if name[:-7].endswith('.'):
            name = name[:-8]
        elif name[:-5].endswith('.'):
            name = name[:-4]
    return name

def get_extension(in_name):
    name = in_name
    if len(name) > 6:
        if name[:-3].endswith('.'):
            name = name[len(name)-4:]
    return name

def handle_beta(path):
    betapath = os.path.join(path,"Beta")
    if not os.path.exists(betapath):
        os.mkdir(betapath)
    with open('beta.txt', 'w') as betalog:
        with os.scandir(path) as entries:
            for entry in entries:
                newname = re.search('\(beta*\)',entry.name, flags=re.IGNORECASE)
                if newname != None:
                    os.rename(entry.path,os.path.join(betapath,entry.name))
                    betalog.write (entry.path + " -> " + os.path.join(betapath,entry.name) + '\n')

def handle_brackets(path):
    duppath = os.path.join(path,"dups")
    if not os.path.exists(duppath):
        os.mkdir(duppath)
    with open('bracket.txt', 'w') as bracketlog:
        with os.scandir(path) as entries:
            for entry in entries:
                newname = re.search(' \(([a-zA-Z])*\)| \[!]',entry.name, flags=re.IGNORECASE)
                if newname != None:
                    t = os.path.join(path, entry.name.replace(newname.group(0),''))
                    if not os.path.exists(t):
                        os.rename(entry.path,t)
                        bracketlog.write('renaming: ' + entry.path  + ' -> '+  t)
                    else:
                        t = os.path.join(duppath,entry.name)
                        os.rename(entry.path,t)
                        bracketlog.write('moving:' + entry.path + ' -> ' + t)

def rename_files(path):
    filenames = []
    otherpath = os.path.join(path,"Other")
    if not os.path.exists(otherpath):
        os.mkdir(otherpath)
    with open('cleanup.txt', 'w') as cleanlog:
        with open('movelog.txt','w') as movelog:
            with open('problemlog.txt','w') as problemlog:
                with open('completedlog.txt','w') as completedlog:
                    with open('problemlog.txt','w') as problemlog:
                        if not os.path.exists(otherpath):
                            os.mkdir(otherpath)
                            cleanlog.write('Created directory ' + otherpath + "\n")
                        with os.scandir(path) as entries:
                            for entry in entries:
                                if not os.path.isdir(os.path.join(path,entry.name)):
                                    cleanup_names(path, filenames, otherpath, cleanlog, entry, movelog, problemlog, completedlog)
    return list(set(filenames))

def cleanup_prefix_suffix(path):
    with os.scandir(path) as entries:
        with open('renamed.txt', 'w') as renamelog:
            for entry in entries:
                if not os.path.isdir(os.path.join(path,entry.name)):
                    ext = get_extension(entry.name).strip()
                    new_name = os.path.join(path,trim_filename(entry.name).strip() + ext)
                    new_name = replace(ext + ext,ext,new_name)
                    while 'the the' in new_name.lower():
                        new_name = replace('the ','',new_name)
                    old_name = os.path.join(path,entry.name.strip())
                    os.rename(old_name,new_name)
                    renamelog.write('Renaming: ' + old_name + ' -> ' + new_name + '\n')


def cleanup_names(path, filenames, otherpath, cleanlog, entry, movelog, problemlog, completedlog):
    if "(j)" not in entry.name.lower():
        cleanup_filenames(path, filenames, cleanlog, entry.name, completedlog, problemlog)
    else:
        if not os.path.exists(os.path.join(otherpath,entry.name)):
            movelog.write('moving: '+ os.path.join(path,entry.name +" -> " + os.path.join(otherpath,entry.name)) + "\n")
            os.rename(os.path.join(path,entry.name), os.path.join(otherpath,entry.name))
        else:
            problemlog.write('problem-other: ' + entry.name + "\n")

def cleanup_filenames(path, filenames, cleanlog, fname, completedlog, problemlog):
    newname = re.sub('\([a-zA-Z!@#$%^&*\[\]]*\)','',fname).lower().replace(' .','.').title().replace('(','').replace(')','').replace(',','.').replace('-',' ').replace('_',' ')
    finalname = space_before_num(newname)
    if ' the.' in fname.lower():
        finalname = 'The ' + replace('the.','',finalname,True)
    finalname = finalname.replace("  "," ").strip()
    if finalname != fname:
        filenames.append(try_rename(path, cleanlog, fname, finalname))
    else:
        completedlog.write('done: ' + fname + "\n")
        filenames.append(trim_filename(fname))

def space_before_num(newname):
    finalname = ''
    firstdigit = True
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
    return finalname

def try_rename(path, cleanlog, fname, finalname):
    if not os.path.exists(path + finalname):
        cleanlog.write("renaming: " + path + fname + " -> " + path + finalname + "\n")
        os.rename(path + fname,path + finalname)
        return trim_filename(finalname)
    else:
        cleanlog.write('not renaming: ' + fname + "\n")
        return ''

def main():
    path = "/home/pete/Downloads/RomsCopy/SNES Roms/"
    handle_beta(path)
    handle_brackets(path)
    filenames = rename_files(path)
    handle_dups(path,filenames)
    cleanup_prefix_suffix(path)
    
if __name__ == "__main__":
    main()