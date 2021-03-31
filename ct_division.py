def uint32_divmod_uint14(x, m):
    '''uint32_divmod_uint14 from supercop:crypto_kem/sntrup761/ref/uint32.c
       constant-time division of a uint32 x / uint14 m, returning
       divmod(x,m) and is constant-time with respect to (x); not (m).

    ... but it looks like it works with m (a lot) > uint14 though, not sure:
    This implementation has been tested for all uint32_t inputs with
    m = 100 000 000 (ie 8 decimal digits)
    m =   1 000 000 (ie 6 decimal digits)
    m =      10 000
    m         1 000
    m =         100
    m =          10
    for m in (10,100,100, .....):
      for x in range(0x100000000):
         assert divmod(x,m) == uint32_divmod_uint14(x, m), f'{x}%{m}'

    BE AWARE that the Python code below does not match the C code 1:1,
    there's likely a uint64/uint32 truncation missing somewhere
    (it fails for m=1 for instance, so you might want to check your target
    parameters before using them).
    '''
    assert 0 <= x <= 0xffffFFFF
    assert (1 < m < 16384) or (m == 1000000) or (m == 100000000)

    v = 0x80000000 // m
    qpart = (x*v) >> 31
    x -= qpart * m
    q = qpart
    qpart = (x * v) >> 31
    x -= qpart * m
    q += qpart + 1
    x -= m
    x &= 0xffffFFFF
    mask = -(x >> 31)
    x += mask & m    # remainder
    x &= 0xffffFFFF
    q += mask        # quotient
    q &= 0xffffFFFF
    return q, x
