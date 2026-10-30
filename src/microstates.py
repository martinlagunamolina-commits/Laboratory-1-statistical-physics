def total_microstates(N: int): 
    return 1 << N

# Calculates 2^N, the total number of configurations without generating them.


def enumerate_microstates(N: int):
    for state in range(1 << N):
        yield state
        
# Generates every microstate as an integer, one at a time, without storing all states in a list.

def count_heads(state: int) -> int:
    heads = 0

    while state > 0:
        if state % 2 == 1:
            heads = heads + 1

        state = state // 2

    return heads

# Counts the 1 bits in a microstate, because each 1 represents a head, by dividing by 2 and getting the reminder, we are effectively reading each bit.


def count_macrostate_multiplicities(N: int) -> dict[int, int]:
    multiplicities = {}

    # Initially, every macrostate has zero microstates.
    for k in range(N + 1):
        multiplicities[k] = 0

    # Generate every microstate and count its heads.
    for state in enumerate_microstates(N):
        k = count_heads(state)
        multiplicities[k] = multiplicities[k] + 1

    return multiplicities

# Groups all generated microstates by their number of heads and counts each group.

