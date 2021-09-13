# Tagged pointers
A loose idea on turning buffer overflows into NULL ptr derefs, for when branching is slow, and overflowing is disastrous.

1) store allocation size in high bits of pointer
2) before deref obtain 1 if in bounds and 0 otherwise, using simple arithmetic (e.g. a perfect hash function calculated at compile-time)
3) multiply pointer by this number before use
