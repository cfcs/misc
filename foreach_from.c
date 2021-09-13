#include <stdio.h>
int main()
{
  #define next(n) (((n)+1) == 10 ? 0 : (n+1))
  #define first() 1
  int self = 3;
  int c = self;

  do {
    printf("id: %d next:%d first:%d\n", c, next(c), first());
  } while ( ((c = next(c)) || (c = first())) && c != self);
  return 0;
}
