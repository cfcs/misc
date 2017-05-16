#!/bin/sh
# usage: unsparsify.sh FILENAME
# makes a sparse file guaranteed to have extents allocated for all of its blocks
# (ensuring that the underlying fs will not be out of disk space when writing to the file)
# it does so by calling the glibc function posix_fallocate()
# basically this is the reverse of "fallocate --dig-holes"
#
# man 3 posix_fallocate
# man 1 fallocate

python -B -c 'import sys,os,ctypes as m;c=m.CDLL("libc.so.6");a=os.open(sys.argv[1],0x501);f=c.posix_fallocate;f.argtypes=[m.c_ulong]*3;print f(a,0,os.lseek(a,0,2))' "$1"

