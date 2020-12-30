/*
gcc ./ocaml-int2bool-experiments.c -o bools && ./bools
random experiments with int -> bool conversions

Here's what we're competing with:

let int2bool (x:int) : bool = x <> 0
camlExample__int2bool_5:
        cmpq    $1, %rax
        setne   %al
        movzbq  %al, %rax
        leaq    1(%rax,%rax), %rax
        ret

let bool2int y = Bool.to_int y
camlExample__bool2int_5:
        cmpq    $1, %rax
        je      .L100
        movl    $3, %eax
        ret
.L100:
        movl    $1, %eax
        ret
(* well this can just be replaced with "ret" ... *)


Essentially it's about mapping
match x with
| n when 0 = n land 1 -> . (* GC bit should be set *)
| 1 -> false
| _ -> true

match y with
| n when 0 = n land 1 -> .
| 1 -> 1
| 3 -> 3
| _ -> .

*/

#include <stdio.h>
#include <stdint.h>
#include <string.h>
int main(){

volatile unsigned long long iin =
     0b1 | /* assume GC bit set */
    0b100000100
;

/*
 * int2bool from ocaml 4.10.0 with flambda
 * compare to 1 (aka zero with gc bit)
 * set lower byte to one if it wasn't $1
 * mov-extend %al (aka clear upper bits of %rax)
 * shift 1, add 1 (aka multiply by 3)
 */
volatile long long test_out = 0;
asm("cmpq $1, %0\n"
    "setne %%al\n"
    "movzbq %%al, %0\n"
    "leaq 1(%0,%0,1), %0\n"
    //"ret\n"
    : "=a"(test_out)
    : "0"(iin));

/*
 * int2bool from this experiment
 * PEXT gathers set bits towards LSB
 * AND truncates to GC bit and is
 * 1 if only GC bit was set
 * 3 if GC and any other bit was set
 */
volatile long long pext_out = 0;
asm("pextq %0, %0, %0\n"
    "andq $0b11, %0\n"
    //"ret\n"
    : "=a"(pext_out)
    : "0"(iin) );

/*
 * If false:   1 (GC bit)
 * If true: 0b11 (1 + GC bit)
 */
const long long expected =
    (((!! /* cast to bool (1 or 0) */
	    (iin & ~1)) /* strip GC bit */
	<< 1)   /* make room for GC bit */
	| 1);   /* set GC bit */

printf(""
    "         iin: %5llu\t = %#0.2llx\n"
    "    pext out: %5llu\t = %#0.2llx\n"
    "    test out: %5llu\t = %#0.2llx\n"
    "expected out: %5llu\t = %#0.2llx\n",
    iin, iin,
    pext_out, pext_out,
    test_out, test_out,
    expected, expected);

return !(pext_out == test_out && test_out == expected);
}
