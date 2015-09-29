// macro for getting a default value (-1 in NUMERIFY) for undefined constants
// if the constants is a value between 0 and 999, that value is returned.
// compile with optimization (gcc -O1 or higher) to evaluate it statically

#include <stdio.h>
#include <errno.h>
#include <stdlib.h>

#define STRINGIFY(a) #a
#define ISNUM(a,i) (STRINGIFY(a)[i] <= 0x39 && STRINGIFY(a)[i] >= 0x30)
#define NUMERIFY(a,i) (ISNUM(a,i) \
                       ? (STRINGIFY(a)[i] & 0xf) : -1 )
#define CASE(a) \
  (ISNUM(a,2) \
  ? (NUMERIFY(a,0) * 100 + (NUMERIFY(a,1) * 10) + NUMERIFY(a,2)) \
  : (ISNUM(a,1) \
    ? (NUMERIFY(a,0) * 10 +  NUMERIFY(a,1)) \
    : NUMERIFY(a,0)))

void main(){

int number = 300;
#define THIS_IS_DEFINED 300


  if( number == CASE(THIS_IS_NOT_DEFINED_ANYWHERE)
   || number == CASE(THIS_IS_DEFINED) )

  printf("yay %d == %d\n", CASE(THIS_IS_DEFINED), number);

  else

  printf("decimal %d != %d , isnum: %d num: %d\n",
    CASE( THIS_IS_NOT_DEFINED_ANYWHERE ),
    number,
    ISNUM(    THIS_IS_DEFINED, 0 ),
    NUMERIFY( THIS_IS_DEFINED, 2 )
  );

}
