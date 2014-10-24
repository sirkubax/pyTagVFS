#!/usr/bin/env python

# the phoenix project

import os
import hashlib
import argparse
import glob
import uuid
import ntpath
import sys
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
    parser.add_argument("-m", "--mount", help="mount [-t tag] into provided [-m dir]. ( default: all tags)  \
                        this can bue combined with read(bulid dictionary) tags form dir [-r] or will \
                        be based on local cache-database of tags")
    parser.add_argument("-U", "--unmount", help="unmount  -m dir. (remove symliknks) ")
    parser.add_argument("-t", "--tags", help="list of comma-separated (\",\") tags")
    return parser


def read_from_tag_file(tag_file):
    """
    Read lines from tag file, parse them, and return list of dictionaries
    """
    t = open(tag_file, 'r')
    result = []
    for line in t.readlines():
        filename, hash, tags = line.strip().split('||')
        tags_list = tags.split(',')
        result.append({'filename': filename, 'hash': hash, "tags": tags_list})
    t.close()
    return result


def readDir(dir):
    """
    Get tag file(s) form dir, read it's content, and buid [tag] -> list_of_files dictionary
    """
    tagdict = {}
    for root, dirs, files in os.walk(dir):
        tag_files_in_dir = getTagFile(dir)
        if len(tag_files_in_dir) > 0:
            for tagfile in tag_files_in_dir:
                current_records = read_from_tag_file(tagfile)
                for record in current_records:
                    filename = os.path.join(dir, record['filename'])
                    for tag in record['tags']:
                        if tag in tagdict.keys():
                            tagdict[tag].append(filename)
                        else:
                            tagdict[tag] = [filename]
    return tagdict


def getTagFile(dir):
    """
    Aquire (or create) tag file
    """
    # todo - in future we will allow multipe .tag.* files,
    tag_files_in_dir = glob.glob(dir + "/.tag.*")
    if len(tag_files_in_dir) > 1:
        print "More than one .tag in %s, consider merging" % dir
    if len(tag_files_in_dir) > 0:
        return tag_files_in_dir
    else:
        fh = open(os.path.join(dir, '.tag.' + str(uuid.uuid4())), 'w+')
        fh.close()
        tag_files_in_dir = glob.glob(dir + "/.tag.*")
        return tag_files_in_dir
    return []


def manage_tag(file_to_be_taged_full_path, tags, function="update"):
    '''
    Patameters
    file_to_be_taged_full_path
    tags
    function: add/update, remove
    '''
    print "Manage Tag: %s" % os.path.dirname(file_to_be_taged_full_path)
    dir = os.path.dirname(file_to_be_taged_full_path)
    file_to_be_taged = ntpath.basename(file_to_be_taged_full_path)
    tag_files_in_dir = getTagFile(dir)
    file_to_be_taged_hash = hashfile(open(file_to_be_taged_full_path, 'rb'), hashlib.sha256())

    if len(tag_files_in_dir) > 0:
        tag_file = tag_files_in_dir[0]
        current_records = read_from_tag_file(tag_file)

        if tag_record_exist(current_records, file_to_be_taged, file_to_be_taged_hash):
            update_tag(file_to_be_taged, file_to_be_taged_hash, tags, tag_file, current_records)
        else:
            write_tag(file_to_be_taged, file_to_be_taged_hash, tags, tag_file)
    else:
        print "no tag file"


def tag_record_exist(current_records, file_to_be_taged, file_to_be_taged_hash):
    return file_to_be_taged in [x['filename'] for x in current_records] and file_to_be_taged_hash in [x['hash'] for x in current_records]


def write_tag(file_to_be_taged, file_to_be_taged_hash, tags, tag_file):
    print "Tag file: %s" % tag_file
    fh_tagfile = open(tag_file, 'a+')
    fh_tagfile.write("%s||%s||%s\n" % (file_to_be_taged, file_to_be_taged_hash, tags))
    print "FileName: %s \t hash: %s  \t TAGGED" % (file_to_be_taged, file_to_be_taged_hash)
    fh_tagfile.close()
    

def update_tag(file_to_be_taged, file_hash, arg_tags, tag_file, current_tags):
    """
    current_tags -> ({'filename': filename, 'hash': hash, "tags": tags_list})
    file_to_be_taged in [x['filename'] for x in current_records] and file_to_be_taged_hash in [x['hash'] for x in current_records]
    """
    print 'update_tag %s' % file_to_be_taged
    new_tag_file_path = archive__crate_new_tag_file(tag_file)
    fh_tagfile = open(new_tag_file_path, 'a+')
    new_tags = arg_tags.split(',')
    for record in current_tags:
        if file_to_be_taged == record['filename'] and file_hash == record['hash']:
            for tag in new_tags:
                if tag not in record['tags']:
                    record['tags'].append(tag)
            print "FileName: %s \t hash: %s  \t UPDATED" % (record['filename'], record['hash'])
        fh_tagfile.write("%s||%s||%s\n" % (record['filename'], record['hash'], ','.join(record['tags'])))
    fh_tagfile.close()


def archive__crate_new_tag_file(tag_file):
    """
    Archive current tag file, create new one
    """
    tag_file_name = ntpath.basename(tag_file)
    dir = os.path.dirname(tag_file)
    os.rename(tag_file, os.path.join(dir, '.hist' + tag_file_name))
    new_tag_file_path = os.path.join(dir, '.tag.' + str(uuid.uuid4()))
    fh = open(new_tag_file_path, 'w+')
    fh.close()
    return new_tag_file_path


def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()


def normalize_a_file_name(fileName):
    fname = ""
    if os.path.isabs(fileName):
        #print "tag absolutePath file"
        fname = fileName
    else:
        #print "tag local filePath file"
        fname = os.path.join(os.getcwd(), fileName)

    if os.path.isfile(fname):
        return fname
    else:
        print "no file %s" % fileName
        return None


def tagDir(dirName):  
    pass


def mount_files(mount_dir, file_list):
    for file in file_list:
        print "Mounting %s" % file
        filename = ntpath.basename(file)
        count = len(glob.glob(os.path.join(mount_dir + filename)))
        print os.path.join(mount_dir + filename)
        print (glob.glob(os.path.join(mount_dir + filename)))
        if count > 0:
            filename += '.' + str(count + 1)
        new_file_name_path = os.path.join(mount_dir, filename)
        print new_file_name_path
        os.symlink(file, new_file_name_path)


if __name__ == '__main__':
    parser = init()
    args = parser.parse_args()
    argsdict = vars(args)
    finaldict = {}
    print "%s \n" % args 
    if args.addtag:
        if args.tags > 0:
            fname = normalize_a_file_name(argsdict['addtag'])
            if fname is not None:
                #writeTag(fname, args.tags)
                manage_tag(fname, args.tags)
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
            print "Mount dir: %s" % args.mount

            (root, dirs, files) = next(os.walk(args.mount))
            if len(dirs) > 0 or len(files) > 0:
                print "Mount directory: %s -  not empty" % args.mount
            else:
                if args.tags:
                    tags = args.tags.split(',')
                    print finaldict
                    for tag in tags:
                        if tag in finaldict.keys():
                            print "Tag:%s | Files: %s" % (tag, finaldict[tag])
                            ''' Add solution for auto-renaming symliks of multiple files with the same file name'''
                            mount_files(args.mount, finaldict[tag])
                            print "Mounted"
                        else:
                            print "Tag:%s | Files: %s" % (tag, 'None')
                else: 
                    print 'Mount all tags - not implemented yet'

    if args.unmount:
        print "unmount"
        symlinks = []
        (root, dirs, files) = next(os.walk(args.unmount))
        for file in files:
            full_path_file = os.path.join(root, file)
            if os.path.islink(full_path_file):
                symlinks.append(full_path_file)

        print "Do you want to unlink following files:"
        print symlinks
        print "yes/no"
        question = sys.stdin.readline()
        if question.strip() == 'yes':
            print "Unlinkikg"
            for file in symlinks:
                os.unlink(file)


                
