#!/usr/bin/env python3
'''Table-based branch-free fizzbuzz implementation based on the
   observation that it is periodic and a sequence of seven strings
   is sufficient to cover the period.
   Since this implementation uses seven divisions as opposed to the 3 in the
   traditional implementation, it's unlikely to be faster.
   An optimization could be to keep the previous state around, but
   doing so would remove the nice closed-form property.
'''

def traditional(i):
    tab = '\t'
    if i % 15 == 0:
        return f'FizzBuzz'
    elif i % 5 == 0:
        return f'Buzz{tab}'
    elif i % 3 == 0:
        return f'Fizz{tab}'
    return f'{i}{tab}'

def branchless(i):
    # this could be a global array:
    arr = ['X', 'Fizz', 'Buzz', 'Fizz', 'Fizz', 'Buzz', 'Fizz', 'FizzBuzz']

    arr[0] = i # so we can print the current number by selecting arr[0]

    # state2: number of fizz+buzz-fizzbuzzes at current i
    # state: number of fizz+buzz-fizzbuzzes at previous i
    state2 = ( (i) // 3 +   (i) // 5 -   (i) // 15)
    state = ((i-1) // 3 + (i-1) // 5 - (i-1) // 15)

    # if the number of interesting states at (i) and i-1 are the same,
    # we infer that (i) is not interesting, and thus (mod) will be 0.
    # otherwise, (mod) is 1:
    mod = state2 - state

    # multiply by (mod) to get either 0 or (1 + state % 7)
    # the +1 will skip the X element, the modulo selects from the sequence
    # of fizz/buzz/fizzbuzz. we could alternatively start at state
    # 3 (making the sequence [Fizz,Buzz,Fizz,FizzBuzz] and skipping every
    # other FizzBuzz):
    return arr[mod*(1 + (state % (len(arr)-1))  )]

    
for i in range(1,101):
    sanity = traditional(i)
    selected = branchless(i)
    print(f'{i}\t{sanity}\t{selected}')
