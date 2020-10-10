#!/usr/bin/env python3
'''Decoder from key-value formatted "structured text" Lotus Notes exports to JSON.
   When run as a script, it takes the optional argument --as-list and a set of exported files.

   Example with --as-list:
   ./lotus-notes-convert.py ./exported1.txt ./exported2.txt --as-list | jq '.[].text'

   Example without --as-list (just concatenated dicts):
   ./lotus-notes-convert.py ./exported1.txt ./exported2.txt | jq '.title'
'''

# quick and dirty version:
#
# a = open('notes_c_user_guide.structured').read()
# for z in map(lambda t: t.split('\ntext:'),  a.split('\x0c')):
#     o = dict(filter(lambda n: len(''.join(n)), map(lambda x: x.split(':', 1), z[0].strip().split('\n'))))
#     o['text'] = z[1:]
#     json.dump(o, sys.stdout)


import json
import sys
import mmap
from contextlib import contextmanager
import chardet
import codecs

RECORD_SEPARATOR = b'\x0C'

@contextmanager
def get_mmap(filename):
    '''Returns an mmap object given a filename'''
    with open(filename, mode=r'r') as fd_handle:
        with mmap.mmap(fd_handle.fileno(), 0, access=mmap.PROT_READ) as fd_mmap:
            fd_mmap.madvise(mmap.MADV_SEQUENTIAL | mmap.MADV_WILLNEED)
            yield fd_mmap
            fd_mmap.close()

def get_chunks(fd_mmap):
    '''Returns a chunk generator given an mmap object.
       The chunk generator handles text codec detection and decoding.
    '''
    encoding = chardet.detect(fd_mmap.read(4))['encoding']
    offset = 0
    stop = 0
    while True:
        stop = fd_mmap.find(RECORD_SEPARATOR, offset)
        if -1 == stop:
            assert offset +1 == fd_mmap.size()-1
            return
        else:
            view = memoryview(fd_mmap)[offset:stop]
            copy = codecs.decode(view, encoding)
            view.release()
            yield copy
            offset = stop + 1
    return

def get_dicts(chunks):
    '''Returns a dict generator given a chunks generator'''
    for dx in chunks:
        header, body = dx.split('\n\ntext:',1)
        if '\n' == header[0]:
            header = header[1:]
        headers = dict(map(lambda line: line.split(':  ', 1), header.split('\n')))
        headers['text'] = body
        yield headers

def dict_generator(filenames):
    for filename in filenames:
        with get_mmap(filename) as fd_mmap:
            for v in get_dicts(get_chunks(fd_mmap)):
                yield v

class SerializableDictGenerator(list):
    '''Wraps dict_generator() in a list-like object to permit serialization.'''
    def __init__(self, filenames):
        self._generator = dict_generator(filenames)
    def __iter__(self):
        return self._generator.__iter__()
    def __len__(self):
        return 1 # Here we lie, which works with the json module, mileage may vary.

def dump_json_stream(filenames, fd_out=sys.stdout, as_list=False):
    '''Dumps a JSON representation of the files on the given
       stream object (e.g. an open file handle).
       Each dict is output individually in "slurp" format, not as a list.
    '''
    if as_list:
        json.dump(SerializableDictGenerator(files), fd_out)
    else:
        for v in dict_generator(files):
            json.dump(v, fd_out)
    fd_out.flush()
    fd_out.close()

if '__main__' == __name__:
    files = list(filter(lambda fn: '--as-list' != fn, sys.argv[1:]))
    as_list = files != sys.argv[1:]
    dump_json_stream(files, as_list=as_list)
