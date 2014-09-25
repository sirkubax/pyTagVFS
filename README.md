pyTagVFS
========

# pyTagVFS = Tag files and build Virtual File System (python)

## Project that covers requirements:
* any file readable by the user can be tagged
* tags are stored "with the files" (in .tag.* file) - in the same dir that tagged file - when you copy directory, you copy tags
* tags are generated + tags are stored with the files -> It will work on any mount point, any computer, any "mount path"
* files can be moved around without losing the previously associated tags (a rebuild-tag option might be required)
* copy/rsync of dirs will not destory tags
* result of "generate-tags" creates local-user-cache database improving performance
* any or all tag can be "mounted" as folder containing matching files = it generates on-demand dir with symlinks (in future - FUSE)
* tagging file generates hash(file) to allow tracking filename change (this can be skipped to fasten the program)

## Future ideas:
* GUI - initial concept - flask app browser with files as icons and click-and-tag system
* nautilus plugin?


## Example of current usage:
Help:

 ~/pyTagVFS/src/pytag.py -h


Tag file:

 ~/pyTagVFS/src/pytag.py -T ~/pyTagVFS/test_dir/a/ab/photoA -t myHoliday


Read tags form dirs:

 ~/pyTagVFS/src/pytag.py -r ~/pyTagVFS/test_dir/a/aa/ ~/pyTagVFS/test_dir/a/ab/



Example (not implemented yet):

Mount(symlinks) tag [-t photo] based on localy-stored-cache [ or tags read from [-r dirs]] into [-m dest_dir]

 ~/pyTagVFS/src/pytag.py -m ~/pyTagVFS/mount_test/ -t photo


similar projects
* https://github.com/marook/tagfs
* http://tmsu.org
* Reading: http://superuser.com/questions/81563/whats-a-good-solution-for-file-tagging-in-linux
