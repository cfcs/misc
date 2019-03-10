#!/usr/bin/env python3

# Python implementation of the LZW decompression function from GIF87a.
# See gif_lzw_decoder.ml for the OCaml implementation.
# The implementation are aligned line-for-line for split-screen reading.

class FINISHED(Exception):  pass
class NEXT(Exception):      pass
class NEED_MORE(Exception): pass

def lzw_stream(v, remain, o, x, lzw_counter, lzw_code_size, lzw_min_size):
    # lzw_code_size: current bitlength we read
    # lzw_counter: the amount of symbols we have read using lzw_code_size
    # lzw_min_size: the original bitlength we read
    # vlw: variable-length word bitlength (lzw_code_size + 1)
    # v:   decompressed value (may be partial, when remain = 0)
    # x:   compressed input string
    # o:   bit offset
    # *)
    char_idx = o // 8
    if char_idx >= len(x):
        raise NEED_MORE()


    vlw = lzw_code_size + 1
    o_mod = o % 8
    current_byte = ord(x[char_idx:char_idx+1]) # <-- Python2/Python3 compat
    if o_mod + vlw <= 8:
        def mask(maske,i): return ((1 << maske) -1) & i
        o = o + remain
        v = (mask(remain,(current_byte >> o_mod)) << (vlw-remain)) | v
        remain = 0
    else:
        vikanta =  8  - o_mod
        o       =  o  + vikanta
        v = ( (current_byte >> (8 - vikanta)) << (vlw - remain)  ) | v
        remain  = vlw - vikanta
    if 0 == remain:
        if v == (1 << lzw_min_size) + 1:
            raise FINISHED()
        else:
            if lzw_counter == (1 << lzw_code_size) -1:
                lzw_counter = 0
                lzw_code_size += 1
            raise NEXT((0, lzw_code_size+1, o, x, lzw_counter+1,
                        lzw_code_size, lzw_min_size), v)
    else:
        lzw_stream(v, remain,o,x,lzw_counter,lzw_code_size, lzw_min_size)


def goparse(buf, lzw_min_size, lzw_code_size):
    try:
        lzw_stream(lzw_min_size=lzw_min_size, remain=(lzw_code_size+1),
            x=buf, lzw_code_size=lzw_code_size, v=0, o=0, lzw_counter=0) ;
        raise Exception("oops")
    except NEXT as y:
        assert y.args[1] == 1 << lzw_min_size, 'incorrect clear code'
        state = y.args[0]
    output_stream = []
    while True:
      try: lzw_stream(*state); raise Exception("the function exceptionally returned")
      except NEXT as y:
          state = y.args[0]
          output_stream.append(y.args[1])
      except FINISHED: return output_stream

def main():
    #print('parsed!', goparse(b'\x84\x1cw\x05', 2, 2))
    #print('parsed!', goparse(b'\x8cP', 2, 2))
    print('parsed!', goparse(b'\x90\x21\x17\xca\x3b\xcd\x00\x25\xc8\x1a\x49\x04', 4, 4))
    raise Exception('loaded')

if __name__ == '__main__':
    main()
