#!/usr/bin/env python

# the phoenix project

import os
import hashlib
import argparse
import glob
import uuid
import ntpath
import fileinput


'''
Ideas
    Directory tag at the begining of .tag file

'''

def init():
    parser = argparse.ArgumentParser(description='pytag')
    parser.add_argument("-r", "--readtags", help='read tags from directory[ies]',  nargs='*', action='append')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-H", "--store-hist-files", help="Store .hist.tag* files", action="store_true")
    parser.add_argument("-e", "--file-ext", help="file extesion (.jpg .png)", action="store_true")
    parser.add_argument("-s", "--skip-hash", help="skip hash coputation")
    parser.add_argument("-f", "--force", help="force merge, possible tag loss")
    parser.add_argument("-R", "--recursive", help="recurse subdirectories")
    parser.add_argument("-F", "--rebuild", help="rebuild .tag [can work with --file-ext and --dir]")
    parser.add_argument("-T", "--addtag", help="file to tag")
    parser.add_argument("-x", "--removetag", help="file to tag")
    parser.add_argument("-d", "--dir", help="list of directories")
    parser.add_argument("-m", "--mount", help="mount -t tag into provided -m dir. [ default: all tags] ")
    parser.add_argument("-t", "--tags", help="list of comma-separated (\",\") tags")

    return parser


def readDir(dir):
    tagdict = {}
    for root, dirs, files in os.walk(dir):
        tag_files_in_dir = getTagFile(dir)
        if len(tag_files_in_dir) > 0:
            for tagfile in tag_files_in_dir:
                t = open(tagfile, 'r')
                for line in t.readlines():
                    filename, hash, tags = line.strip().split('||')
                    filename = os.path.join(dir, filename)
                    for tag in tags.split(','):
                        if tag in tagdict.keys():
                            tagdict[tag].append(filename)
                        else:
                            tagdict[tag] = [filename]
                t.close()
    return tagdict


def getTagFile(dir):       
    # todo - in future we will allow multipe .tag.* files, 
    tag_files_in_dir = glob.glob(dir + "/.tag.*")
    #print tag_files_in_dir
    if len(tag_files_in_dir) > 1:
        print "More than one .tag in %s, consider merging" % dir
    if len(tag_files_in_dir) > 0:
        return tag_files_in_dir
    else:
        #return openTagFile(dir)
        os.path.join(dir, '.tag.' + str(uuid.uuid4()), 'w+')
        tag_files_in_dir = glob.glob(dir + "/.tag.*")
        return tag_files_in_dir
    return []


def buildDirFormTag():
    print "CreatingDirTag"
    for root, dirs, files in os.walk(default_dir):
        tagFile = getTag(root)
        print root
        print dirs
        print files
        for line in tagFile.readlines():
            print line.strip()
 

def writeTag(file_to_be_taged_full_path, tags):
    print "WriteTag: %s" % os.path.dirname(file_to_be_taged_full_path)
    dir = os.path.dirname(file_to_be_taged_full_path)
    tag_files_in_dir = getTagFile(dir)
    if len(tag_files_in_dir) > 0:
        writeTagHelper(file_to_be_taged_full_path, tags, tag_files_in_dir)
    else:
        print "no tag file"


def writeTagHelper(file_to_be_taged_full_path, tags, tag_files_in_dir):
    print "Tag file: %s" % tag_files_in_dir[0]
    fh_tagfile = open(tag_files_in_dir[0], 'a+') 
    existingTagLines = fh_tagfile.read()
    file_to_be_taged_hash = hashfile(open(file_to_be_taged_full_path, 'rb'), hashlib.sha256())

    file_to_be_taged = ntpath.basename(file_to_be_taged_full_path)

    # add solution for file with the same hash but changed filename (and reverse) !!!
    if file_to_be_taged_hash in existingTagLines and file_to_be_taged in existingTagLines:
        print "FileName: %s \t hash: %s \t EXIST" % (file_to_be_taged, file_to_be_taged_hash)
        if updateTag(file_to_be_taged, tags, tag_files_in_dir, file_to_be_taged_hash):
            print "FileName: %s \t hash: %s \t UPDATED" % (file_to_be_taged, file_to_be_taged_hash)
        pass
    else:
        fh_tagfile.write("%s||%s||%s\n" % (file_to_be_taged, file_to_be_taged_hash, tags))
        print "FileName: %s \t hash: %s  \t TAGGED" % (file_to_be_taged, file_to_be_taged_hash)
    fh_tagfile.close()


def updateTag(file_to_be_taged, arg_tags, tag_files_in_dir, file_hash):
    print "Command line tags: %s" % arg_tags

    #make a funcion out of this:
    dir = os.path.dirname(tag_files_in_dir[0])
    new_tag_file_path_name = os.path.join(dir, '.new.tag.' + str(uuid.uuid4()))
    fh_new_tag_file = open(new_tag_file_path_name, 'w+')
    fh_current_tag_file = open(tag_files_in_dir[0])

    for line in fh_current_tag_file.readlines():
        if file_to_be_taged in line and file_hash in line:
            print "Current line: %s" % line.strip()
            filename, hash, existingtags = line.strip().split('||')
            new_tags = arg_tags.split(',')
            present_tags = existingtags.split(',')
            final_tags = list(present_tags)
            print 'Present tags: %s\n' % (present_tags) 
            #Should we match on the file name only?
            if file_hash in line and file_to_be_taged in line:
                for tag in new_tags:
                    if tag in present_tags:
                        print "Tag: %s, exist in %s" % (tag, present_tags)
                    else:
                        print "Tag: %s, DOES NOT exist in %s" % (tag, present_tags)
                        final_tags.append(tag)
            #print 'finalTags %s, presentTags %s' % (len(final_tags), len(present_tags)) 
            #print 'present_tags %s' % present_tags

            if len(final_tags) > len(present_tags):
                print 'Final Tags: %s' % final_tags
                final_tags_string = ','.join(final_tags)
                #print 'Final Tags %s' % final_tags_string
                fh_new_tag_file.write("%s||%s||%s\n" % (file_to_be_taged, file_hash, final_tags_string))
            else:
                fh_new_tag_file.write(line)
            print "\n"
        else:
            fh_new_tag_file.write(line)

    fh_new_tag_file.close()
    fh_current_tag_file.close()
    tag_file_name = ntpath.basename(tag_files_in_dir[0])
    new_tag_file_name = ntpath.basename(new_tag_file_path_name)
    hist_files = glob.glob(dir + "/.hist.tag.*")
    os.rename(tag_files_in_dir[0], os.path.join(dir, '.hist' + tag_file_name))
    os.rename(new_tag_file_path_name, os.path.join(dir, '.' + new_tag_file_name.strip('.new')))
    for i in hist_files:
        os.remove(i)
    return False


def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()


def tag_a_file(fileName, tags):  
    #print os.getcwd()
    fname = ""
    if os.path.isabs(fileName):
        #print "tag absolutePath file"
        fname = fileName
    else:
        #print "tag local filePath file"
        fname = os.path.join(os.getcwd(), fileName)
    if os.path.isfile(fname):
        writeTag(fname, tags)
    else:
        print "no file %s" % fileName


def tagDir(dirName):  
    pass


if __name__ == '__main__':
    parser = init()
    args = parser.parse_args()
    argsdict = vars(args)
    finaldict = {}
    print "%s \n" % args 
    if args.addtag:
        if args.tags > 0:
            tag_a_file(argsdict['addtag'], args.tags)
        else:
            print "No -t tags provided"
    if args.readtags:
        #print args.readtags
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
                    
        for key in finaldict:
            print "%s %s" % (key, finaldict[key])
        print

    if args.mount:
        #if args.readtags:
            print args.mount
            #finaldict = {}
            #for dir in args.readtags[0]:
            #    tagdict = readDir(dir)

            if args.tags:
                tags = args.tags.split(',')
                for tag in tags:
                    if tag in tagdict.keys():
                        print "Tag:%s | Files: %s" % (tag, tagdict[tag])
                        for file in tagdict[tag]:
                            #ln -s
                            filename = ntpath.basename(file)
                            new_file_name_path = os.path.join(args.mount, filename)
                            print new_file_name_path
                            os.symlink(file, new_file_name_path)
                            
                    else:
                        print "Tag:%s | Files: %s" % (tag, 'None')
            else: 
                print 'all tags'
                
