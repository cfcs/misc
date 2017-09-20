/**
 * Compute fast bitwise xor between two bit-vectors a, b of n bits,
 * where n is a multiple of 128.
 * Place the result in a.
 */
static inline
void bitxor_m128i(void *_a, const void *_b, size_t n)
{
  assert(n % 128 == 0);

  __m128i *a = (__m128i *) _a;
  __m128i *b = (__m128i *) _b;

  n >>= 7;
  while (n--) {
    *a = _mm_xor_si128(*a, *b);
    ++a; ++b;
  }
}

/**
 * Compute bitwise xor between to bit-vectors a, b of n bits,
 * where n is a multiple of 8.
 * Place the result in a.
 */
static inline
void bitxor_small(void *_a, const void *_b, const size_t _n)
{
  size_t n = _n;
  uint8_t *a = (uint8_t *) _a;
  uint8_t *b = (uint8_t *) _b;

  n >>= 3;

  /* round to the closest multiple of 8-bits */
  if (_n & 7) n++;

  while (n--) {
    *a ^= *b;
    a++; b++;
  }
}


static inline
void bitxor(void *_a, const void *_b, const size_t n)
{
  uint8_t *a = (uint8_t *) _a;
  uint8_t *b = (uint8_t *) _b;
  const size_t small = n % 128;
  const size_t big = n - small;

  bitxor_m128i(a, b,  big);
  bitxor_small(a+big, b+big, small);
}


