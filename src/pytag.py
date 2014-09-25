#!/usr/bin/env python

# the phoenix project

import os
import hashlib
import argparse
import glob
import uuid
import ntpath


'''
Ideas
    Directory tag at the begining of .tag file

'''

def init():
    parser = argparse.ArgumentParser(description='pytag')
    parser.add_argument("-r", "--readtags", help='read tags from directory[ies]',  nargs='*', action='append')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-e", "--file-ext", help="file extesion (.jpg .png)", action="store_true")
    parser.add_argument("-s", "--skip-hash", help="skip hash coputation")
    parser.add_argument("-f", "--force", help="force merge, possible tag loss")
    parser.add_argument("-R", "--recursive", help="recurse subdirectories")
    parser.add_argument("-F", "--rebuild", help="rebuild .tag [can work with --file-ext and --dir]")
    parser.add_argument("-T", "--tagfile", help="file to tag")
    parser.add_argument("-d", "--dir", help="list of directories")
    parser.add_argument("-m", "--mount", help="mount -t tag into provided -m dir. [ default: all tags] ")
    parser.add_argument("-t", "--tags", help="list of tags")

    return parser


def readDir(dir):
    #print "ReadDir"
    tagdict = {}
    for root, dirs, files in os.walk(dir):
        #tagdirlist = glob.glob(dir + "/.tag.*")
        tagfile, tagnum, tagdirlist = getTagFile(dir, 'r')

        if len(tagdirlist) > 0:
            for tagfile in tagdirlist:
                t = open(tagfile, 'r')
                for line in  t.readlines():
                    filename, hash, tags = line.strip().split('||')
                    filename = os.path.join(dir, filename)
                    for tag in tags.split(' '):
                        if tag in tagdict.keys():
                            tagdict[tag].append(filename)
                        else:
                            tagdict[tag] = [filename]
                #print tagdict
                t.close()
    return tagdict


def openTagFile(dir):       
    #check if /dir/.tag file exist, if no, create, if yes, in future we would like to create .tag.tmp and merge it with .tag 
    # .tag.UUID will be introduced to avoid tag lost on cp/rsync of directory. You can merge .tag.* files into one by merge command
    return open(os.path.join(dir, '.tag.' + str(uuid.uuid4()) ), 'w+')


def getTagFile(dir, perm = 'a+'):       
    #todo - in future we will allow multipe .tag.* files, 
    dirlist = glob.glob(dir + "/.tag.*")
    print dirlist
    if len(dirlist) == 1:
        return open(dirlist[0], perm), 1, dirlist
    elif len(dirlist) > 1:
        return open(dirlist[0], perm), len(dirlist), dirlist
    else:
        #return openTagFile(dir)
        perm = 'w+'
        return open(os.path.join(dir, '.tag.' + str(uuid.uuid4()) ), perm), 0, []
    return "empty", 0, []


def buildDirFormTag():
    print "CreatingDirTag"
    for root, dirs, files in os.walk(default_dir):
        tagFile = getTag(root)
        print root
        print dirs
        print files
        for line in tagFile.readlines():
            print line.strip()
 

def writeTag(myfile, tags):
    print "WriteTag: %s" % os.path.dirname(myfile)
    dir = os.path.dirname(myfile)
    tagfile, tagnum, tagdirlist  = getTagFile(dir)
    if tagfile != 'empty':
        writeTagHelper(myfile, tags, tagfile, tagdirlist)
    else:
        print "no tag file"
    tagfile.close()


def writeTagHelper(filetotag, tags, tagfile, tagdirlist):
    #check if sha256 and filename already exist in .tag.* file
    if len(tagdirlist) > 1:
        pass
        #merge .tag.* files into one
    
    existingTags = tagfile.read()
    #print existingTags
    fileHash = hashfile(open(filetotag, 'rb'), hashlib.sha256())

    filetotag = ntpath.basename(filetotag)
    #add solution for file with the same hash but changed filename (and reverse)
    if fileHash in existingTags and filetotag in existingTags:
        print "FileName: %s \t hash: %s \t EXIST" % (filetotag , fileHash )
        pass
    else:
        tagfile.write("%s||%s||%s\n" % (filetotag, fileHash, tags) )
        print "FileName: %s \t hash: %s  \t TAGGED" % (filetotag , fileHash )


def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()


def tagFile(fileName, tags):  
    #print os.getcwd()
    fname = ""
    if os.path.isabs(fileName):
        #print "tag absolutePath file"
        fname = fileName
    else:
        #print "tag local filePath file"
        fname = os.path.join(os.getcwd(), fileName)
    if os.path.isfile(fname):
        print "file exist"
        writeTag(fname, tags)
    else:
        print "no file %s" % fileName


def tagDir(dirName):  
    pass


if __name__ == '__main__':
    print 'start'
    parser = init()
    args = parser.parse_args()
    argsdict = vars(args)
    print args
    if args.tagfile:
        tagFile(argsdict['tagfile'], "aaa bbb")
    if args.readtags:
        #print args.readtags
        finaldict = {}
        for dir in args.readtags[0]:
            #print dir
            #check if dir exist
            tagdict = readDir(dir)
            #print tagdict
            for key in tagdict:
                if key in finaldict.keys():
                    for item in tagdict[key]:
                        finaldict[key].append(item)
                else:
                    finaldict[key] = (tagdict[key])
                    
        print "\n" 
        for key in finaldict:
            print "%s %s" % (key, finaldict[key])

    if args.mount:
        if len(args.mount) == 1:
            print args.mount
            if args.tags:
                for tag in args.tags:
                    print tag
            else: 
                print 'all tags'
                

    #readDir()
    #buildDirFormTag()
    #tagFile('20130618_180331.jpg')
    #tagFile('/home/kuba/pytag/test_dir/20130618_180331.jpg')
