#!/usr/bin/env python2
# python2 -c "
window=60;k_str='74AP6AASGRLHREAR';digits=5;import base64,struct,time;k=(base64.b32decode(k_str,True)+'\x00'*128)[:128];T=struct.pack('>Q',int(time.time())/window);from hashlib import sha512;xor=(lambda a,b:''.join([chr(ord(a[i])^ord(b[i]))for i in range(len(b))]));h=sha512(xor(k,'\x5c'*128)+sha512(xor(k,'\x36'*128)+T).digest()).digest();O=ord(h[-1])&0xf;i=(struct.unpack('>L',h[O:O+4])[0]&0x7FFFFFFF);print ('0'*digits+str(i%10**digits))[-digits:]
# "

# python3 -c 'm=b"a";k=b"b";from hashlib import sha512;L=len(k);k=L<=128 and k+bytes(128-L) or sha512(k).digest();xor=(lambda a,b:bytes([a[i]^b[i]for i in range(len(b))]));h=sha512(xor(k,b"\x5c"*128)+sha512(xor(k,b"6"*128)+m).digest()).hexdigest();print(h)'
