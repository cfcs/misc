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

def branchless_alt(i):
    # this could be a global array:
    arr = ['X', 'FizzBuzz', 'Fizz', 'Buzz', 'Fizz']

    # state2: number of fizz+buzz-fizzbuzzes at current i
    # state: number of fizz+buzz-fizzbuzzes at previous i
    state2 = ( (i) // 3 +   (i) // 5 -   (i) // 15)
    state = ((i-1) // 3 + (i-1) // 5 - (i-1) // 15)

    arr[0] = i # so we can print the current number by selecting arr[0]

    # if the number of interesting states at (i) and i-1 are the same,
    # we infer that (i) is not interesting, and thus (mod) will be 0.
    # otherwise, (mod) is 1:
    mod = state2 - state

    # idx selects our indice into the 7-element sequence:
    idx = (state2 % 7)
    # mod4 shrinks the sequence to four elements, then skips every other
    # FizzBuzz by adding idx/4, letting us distinguish between 0 and 4
    mod4 =  (idx % 4) + idx//4
    return arr[mod*(1+mod4)]

def generative(i):
    '''
    In this alternative version we refrain from doing division in the yield
    loop; cycling through states instead.
    Another implementation idea would be to keep counters for 3 and 5;
    that would probably be a more efficient way to write generators.
    '''
    # mods keeps track of FizzBuzz patterns, starting at 0, which means
    # the (i) argument should be > 0.
    mods = [1,0,0,1,
            0,1,1,0,
            0,1,1,0,
            1,0,0]
    arr = ['X', 'FizzBuzz', 'Fizz', 'Buzz', 'Fizz']
    state2 = ( (i) // 3 +   (i) // 5 -   (i) // 15)
    state_ptr = i % (len(mods))
    arr[0] = i
    idx = state2 % 7
    while True:
        # mod_idx = 1 + idx%4 + idx//4
        # { idx < 7 -> 1 <= mod_idx <= 5}
        mod_idx = 1 + (idx & 3) + (idx >> 2)
        yield arr[mods[state_ptr] * mod_idx]

        # state_ptr = (state_ptr + 1 ) % len(mods)
        # state_ptr = (state_ptr + 1 ) % 15:
        state_ptr += 1 # now it may be 15
        # if 15 then 15+1 == ((16 & 16)/16 = 1) -> (state_ptr *= 0):
        state_ptr *= 1 - (((state_ptr + 1) & 16)>>4)

        idx += mods[state_ptr]
        idx *= 1 - ((idx+1) >> 3) # idx = idx % 7
        # idx is only used to compute mod_idx, so some smarter bithackery
        # here could probably trim this section down a bit.

        # update the number to print when not FizzBuzz:
        arr[0] += 1

gen_fizzbuzz = generative(1)
for i in range(1,101):
    sanity = traditional(i)
    selected = branchless(i)
    selected_alt = branchless_alt(i)
    generated = gen_fizzbuzz.send(None)
    generative_check = generative(i).send(None)
    print(f'{i}\t{sanity}\t{selected}\t{selected_alt}\t{generated}\t{generative_check}'.replace('FizzBuzz','\x1b[31mFIZZBUZZ\x1b[0m').replace('Buzz','\x1b[32mBUZZ\x1b[0m').replace('Fizz','\x1b[33mFIZZ\x1b[0m'))
