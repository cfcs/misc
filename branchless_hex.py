#!/usr/bin/python3
'''Branchless encoding/decoding of hexadecimal to/from bytes
   without using tables
see also
https://stackoverflow.com/a/34366370
which has cooler stuff
'''

# for i in [48,49,50,51,52,53,54,55,56,57,97,98,99,100,101,102]: x=(i+39-1-54); x=x&(~0x20); y=x-(((x&16)>>4)*71); print(i, hex(x),x, hex(y), y) # 6 operations per nibble

def p(n):
  '''right-pad'''
  return '\t'+' '*(9-len(str(n)))+str(n)

def out_digit(f):
  '''select 0..9 a..f from integer'''
  #a=(f >> 1);a=(a&0b11)*(a&100)
  #a=((a&0b100)>>2) | (a>>3); #    0    ,  1

  # a=(f&0b110)>>(1+(~f&8));b=0x2f*((a>>1|a)&1)+0x30+(f&7);
  # for f in range(0,16): a=(86+f);c=1+(a-71*((a&0x10)>>4))|0x20; print(f, a, '\t', bin(a), a, hex(c))# 7 operations per nibble -1 for the |0x20 which could be |0x20x20
  a = (f + 14) >> 3
  #b = (f + 14)
  #b = (f+38) >> 1
  #b = ((b&10)) << 2
  #print(f, p(bin(b)[2:]), b, b&24)
  a = a & (a>>1)

  d=(f&7)-a                  # 0..7 -0 ,  2..7 -1
  d = d +((f&8)>>a*4)        # 8..9>>0 , (10..15 & 8=8)>>4
  c= d + (0x30 << a)         # 0x30 +d , 0x60+d
  #c=(d+0x30 ) + (a << 4)        # 0x30 +d, 0x40+d
  #c=(d | 0x30) + (a << 5 | a<<4)        # 0x30 +d, 0x40+d
  print (f,((f*1) & 0b1110), p(bin(f)),p(a),d,p(bin(a)),c,p(bin(c)),chr(c))
  return chr(c)


for f in range(0,16):
  out_digit(f)
