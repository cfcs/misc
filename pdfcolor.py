#!/usr/bin/env python3
'''Adds text color to a PDF, best-effort. Written to aid in printing on a printer out of black ink.
   Usage: pdfcolor.py input.pdf > output.pdf
   NB: It also inadvertantly applies zlib compression to all objects that it sees.
   It only handles objects whose length/filter/>> directives are on individual
   lines, because that's what my PDF looked like.
'''
import os
import zlib
import sys
import re

def process(fn):
    f = open(fn,'rb').readlines()
    length = 0
    state = 0 # 0: headers, 1: first line after >>, 2: payload body
    buf = b''
    filtr = ''
    last_was_close = False
    last_was_stream = False
    is_first = False
    for lin in f:
        if 1 == state:
            state = 2
            if b'stream\n' == lin:
                assert length
                last_was_stream = True
                continue
        if state:
            out = lin[:length]
            length -= len(out)
            buf += out
            if length <= 0:
                plain = buf
                if 'FlateDecode' in filtr: # assume only one, can be wrapped in [] for example
                    plain = zlib.decompress(buf)
                if b'BT\n' in plain:
                    # This is where the magic happens
                    # - add rgb color to text:
                    plain = b'.8 0 0 rg\n' + plain
                deflated = zlib.compress(plain)
                os.write(1, b'/Length ' + str(len(deflated)).encode('latin1') + b'\n')
                os.write(1, b'/Filter [/FlateDecode]\n')
                os.write(1, b'>>\n')
                if last_was_stream:
                    os.write(1, b'stream\n')
                    last_was_stream = False
                assert len(deflated) == os.write(1, deflated)
                os.write(1, b'\n')
                state = 0
                buf = b''
                filtr = ''
        else:
            if last_was_stream:
                last_was_stream = False
            if b'>>\n' == lin:
                last_was_close = True
                if length:
                    state = 1
                    is_first = True
                else:
                    filtr = ''
            elif lin.startswith(b'/Length '):
                lengthlist = lin.decode('latin1').strip().split(' ')
                if len(lengthlist) == 2:
                    length = int(lengthlist[1])
                else:
                    # ignore line-based: if lengthlist[-1] == 'R':
                    assert False
            elif lin.startswith(b'/Filter'):
                filtr = re.split('[ /]', lin.decode('latin1')[1:].strip())[1:]
            else:
                if last_was_close:
                    os.write(1, b'>>\n')
                    last_was_close = False
                os.write(1, lin)

if '__main__' == __name__:
    fn = sys.argv[1]
    process(fn)
