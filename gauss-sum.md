# Gauss summation

A note on rewriting summations using the sigma/sum operator from math papers to  code, expanding to avoid expensive loops.

**Note** that the lower and upper bounds are both *inclusive*, unlike Python's `range()` operator which defines a range from a lower bound (inclusive) to an upper bound (exclusive). That means when we see a sigma summation (`6 S i=1`) we need to add one to include the upper bound: `range(1,6+1)`.

```
  6
  S  i*7
 i=0
```
is equivalent to
```python
sum(( i*7 for i in range(0, 6+1) ))
# == 105
# aka
S = 0
for i in range(0, 6+1):
  S = S + i*7
```

<hr>

```
  10
   S   i*7
   5
```
is equivalent to
```python
sum(( i*7 for i in range(5, 10+1) ))
# aka
S = 0
for i in range(5, 10+1):
  S = S + i*7
```

<hr>

Gauss summation can be used to calculate the sum without looping:
```python
def gauss(n):
  # floored division, e.g you can use >> 1 instead of division.
  return n*(n+1) // 2

6+5+4+3+2+1
# 21
sum(( i for i in range(0, 6+1) ))
# 21
gauss(6)
# 21
```

If the loop doesn't start at `1`, the Gauss sum of the numbers below the starting point can be subtracted to yield the sum of the numbers in the range:

```python
10+9+8+7+6+5+4+3+2+1
# 55

4+3+2+1
# 10

55 - 10
# 45

10+9+8+7+6+5
# 45

sum(( i for i in range(5, 10+1) ))
# 45

gauss(10) - gauss(4)
# 45
```

<hr>

Multiplying the added constants by the number of sums (the differene between the top and bottom bound) allows us to derive a closed-form formula for expressions like
```
  10
   S  100 + i
   5
```

```python
gauss(10) - gauss(4)
# the "i" factor = 45

(10 - 4) * 100
# 600

45 + 600
# 645

sum(( 100 + i for i in range(5, 10+1) ))
# 645
```

Similarly, products depending on the `i` factor can be multiplied by the sum:
```
  10
   S  i * 12  + 34
   5
```

```python
10+9+8+7+6+5
# 45

45 * 12
# 540

(10-4) * 34
# 204

540 + 204
# 744

sum(( i*12 + 34 for i in range(5, 10+1) ))
# 744

(gauss(10) - gauss(4)) * 12  +  (10-4) * 34
# 744
```

If we frequently need to compute the sum of intervals that do not start at `1` we can improve on the
`gauss(upper) - gauss(lower-1)` formula to lower the number of arithmetic operations from `7 (3+3+1)` to `5`:

```python
def gauss(n):
  # floored division, e.g you can use >> 1 instead of division.
  return n*(n+1) // 2
  
def gauss_i(lower, upper):
  return ((upper - lower + 1) * (lower+upper)) // 2

gauss_i(5,5)
# 5

5+4+3
gauss(5)-gauss(3-1)
((5-3+1)*(3+5))/2
gauss_i(3,5)
# 12

5+4
gauss(5)-gauss(4-1)
gauss_i(4,5)
# 9
```

<hr>

This lets us calculate our "complex" summation
```
  10
   S  i * 12  + 34
   5
```
as follows:
```python
gauss_i(5,10) * 12 + (10-5+1) * 34
# 744
```

If we know the arguments up front we can specialize it for our scenario.

### Constant loop bounds
```python
a = 12
b = 34

(((10 - 5 + 1) * (5+10)) // 2) * a + (10-5+1) * b
# 744

(((6) * (15)) // 2) * a + (6) * b
# 744

45 * a + 6 * b
# 744
```

### Variable loop bounds, constant loop bodyy
```python
low = 5
high = 10

(((high - low + 1) * (low+high)) // 2) * 12     + (high-low+1) * 34
# 744, 10 operations

((((high - low + 1) * (low+high))) * (12 // 2)) + (high-low+1) * 34
# 744

(high - low + 1) * (low+high) * 6               + (high-low+1) * 34
# 744, 9 operations
# here we got rid of the division. one of the bounds are known,
# we can expand it more aggressively.
# below are some notes for that:

#   (high - low + 1) * (low+high) * 6
# + (high - low + 1) * 34
(   (high - low) * (low+high) * 6
    + 1 * (low+high) * 6
  + (high - low) * 34
    + 1 * 34
)
# 744, 13 operations

( (high - low) * (low+high) * 6
    + low * 6
    + high * 6
  + high * 34
    - low * 34
    + 34
)
# 744, 13 operations

( (high - low) * (low+high) * 6
    + high * 40
    - low * 28
    + 34
)
# 744, 9 operations again

(   (high*low - low*low)*6
  + ((high*high - low*high)*6)
 + high * 40
 - low * 28
 + 34
)
# 744, 14 operations

(   6*high*low 
  - 6*low*low
  + 6*high*high
  - 6*high*low
 + high * 40
 - low * 28
 + 34
)
# 744, 16 operations

( 6*(high*high - low*low)
 + high * 40
 - low * 28
 + 34
)
# 744, 9 operations, easily shortened if (high) or (low) are known.

# if we allow for floating-point arithmetic:
6*( high*high
   - low*low
   + high * 40/6
   - low * 28/6 # 
   + 34/6
  )
# ~~~ 744 ~~~ 9 operations
```

For instance, given a lower bound of 0:
```
  x
  S    i * 12  + 34
  i=0
```
We can apply this:
```python
x = 10

(6 * (x*x - 0*0)
  + x*40
  - 0 * 28
  + 34
)
# 1034

(6 * (x*x) + x*40 + 34)
# 1034
```

And a lower bound of 1:
```python
x = 10

(6 * (x*x - 1*1)
  + x*40
  - 1 * 28
  + 34
)
# 1000

(6 * (x*x - 1)
  + x*40
  + 6
)
# 1000

6 * x * x + 40 * x
# 1000
```

Now go eradicate those for-loops! :-)

<hr>

PS:

### Nested sums

We can work with nested/recursive summations too:

```
   2  (  6
   S  (  S   (3ij)
  i=1 ( j=4

aka
  i   j (3ij)
  1   4   12
  1   5   15
  1   6   18
  2   4   24
  2   5   30
  2   6   36
          ---
          135
          ===
```
(in Python):
```python
S = 0
for i in range(  1, 2+1):
  for j in range(4, 6+1):
    S = S + 3*i*j
# 135
```

by first rewriting the innermost summation:
```python
#  6
#  S   (3 * j)
# j=4

6*3 + 5 * 3 + 4*3
# 45

gauss_i(4,6) * 3
# 45
```

then the second can be expressed as a single loop:
```python
S = 0
for i in range(  1, 2+1):
  S = S + gauss_i(4,6) * 3 * i
# 135
```
substituting the formula for `gauss_i` we get
```
  2
  S    3 * i * (((6 - 4 + 1) * (4+6)) // 2)y
 i=1

<=>
  2
  S    3 * i * 15
 i=1
<=>
  2
  S    45 * i
 i=1
```

Which we can then translate to Python:
```python
gauss_i(1,2) * 45
```

<hr>

A slightly more advanced example:
```
  200    (  60
   S     (   S    3 * i * j + i*5 + j * 6 + 1337
  i=100  (  j=40
```
in Python:
```python
S = 0
for i in range(100, 200+1):
  for j in range(40, 60+1):
    S = S + 3*i*j + 5*i + 6*j + 1337
# 52785327
# or with generator expressions:
sum((
   (3 * i * j + 5*i + 6*j + 1337)
   for j in range(40, 60+1)
   for i in range(100, 200+1)
))
# 52785327
```
again we start with the inner loop, pretending that `i=1` and that components that only depend on `i` are constants:
```python
i = 1
sum((
  (3 * i * j + i*5 + 6*j + 1337)
  for j in range(40, 60+1)
))
# 37632

( # 3 * i * j
  3 * i * gauss_i(40,60)
) + ( # + i*5     , constant multiplied by element count
  (60-40+1) * i * 5
) + (# + 6 * j    , substitute (j) by the sum
  6 * gauss_i(40,60)
) + ( # + 1337    , multiply by element count
  (60-40+1) * 1337
)
# 37632

S = 0
for i in range(100, 200+1):
  S = S + (3 * i * gauss_i(40,60)
  ) + ((60-40+1) * i * 5
  ) + (6 * gauss_i(40,60)) + (
  (60-40+1) * 1337)
# 52785327
```

And now we can expand for the `i`:
```python
j_low = 40
j_high = 60
j_el_count = (j_high - j_low + 1)

i_low = 100
i_high = 200
i_el_count = (i_high - i_low + 1)

( # j_el_count * 1337      ,   constant, multiply by element count:
  i_el_count * (j_el_count * 1337)
) + (
  # 5 * j_el_count * i     ,   substitute gauss_i for i:
  (5 * j_el_count) * gauss_i(i_low, i_high)
) + (
  # 3*i*j                  ,   substitute gauss_i for both i and j:
  3 * gauss_i(i_low,i_high) * gauss_i(j_low, j_high)
) + (
 # 6*j                     ,   multiply by element count:
 i_el_count * 6 * gauss_i(j_low, j_high)
)
# 52785327
```
And thus we have reached a closed-form formula.
We can reduce the number of arithmetic operations slightly by further rewriting the expressions, for example `6 * (.... / 2) => 3 * ( .... )` in the last term; but I thought this was the clearest representation of the original problem.
