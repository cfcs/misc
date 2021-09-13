# Gauss summation

A note on rewriting summations using the sigma/sum operator from math papers to  code, expanding to avoid expensive loops.

**Note** that the lower and upper bounds are both *inclusive*, unlike Python's `range()` operator which defines a range from a lower bound (inclusive) to an upper bound (exclusive). That means when we see a sigma summation (`6 S i=1`) we need to add one to include the upper bound: `range(1,6+1)`.

```
  6
  S  i*7
 i=0
```
is equivalent to
```python3
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
```python3
sum(( i*7 for i in range(5, 10+1) ))
# aka
S = 0
for i in range(5, 10+1):
  S = S + i*7
```

<hr>

Gauss summation can be used to calculate the sum without looping:
```python3
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

```python3
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

```python3
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

```python3
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

```
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
```python3
gauss_i(5,10) * 12 + (10-5+1) * 34
# 744
```

If we know the arguments up front we can specialize it for our scenario.

### Constant loop bounds
```python3
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
```python3
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
```python3
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
```python3
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
