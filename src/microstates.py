"""Stream integer-encoded microstates: 1 represents heads, 0 tails."""

from collections.abc import Iterator


def validate_n(N: int) -> None:
    """Reject noninteger or negative system sizes, including booleans."""
    if isinstance(N, bool) or not isinstance(N, int) or N < 0:
        raise ValueError("N must be a nonnegative Python integer.")


def total_microstates(N: int) -> int:
    """Return the exact count 2**N without enumerating configurations."""
    validate_n(N)
    return 1 << N


def enumerate_microstates(N: int) -> Iterator[int]:
    """Yield every configuration once, using O(N) bits of live state storage."""
    validate_n(N)
    for state in range(1 << N):
        yield state


def count_heads(state: int) -> int:
    """Count set bits by repeatedly clearing the lowest set bit."""
    if isinstance(state, bool) or not isinstance(state, int) or state < 0:
        raise ValueError("state must be a nonnegative Python integer.")
    heads = 0
    while state:
        state &= state - 1
        heads += 1
    return heads


def state_string(state: int, N: int) -> str:
    """Convert an integer state into exactly N H/T symbols."""
    validate_n(N)
    if isinstance(state, bool) or not isinstance(state, int) or not 0 <= state < (1 << N):
        raise ValueError("state must fit in N bits.")
    return "".join("H" if (state >> bit) & 1 else "T" for bit in reversed(range(N)))

def count_heads_fast(state: int) -> int:
    return state.bit_count()
#Uses a pyhton implementation to count bits directly.


def count_macrostate_multiplicities(N: int) -> dict[int, int]:
    """Enumerate all 2**N states and group them by their heads count (small N)."""
    validate_n(N)
    result = dict.fromkeys(range(N + 1), 0)
    for state in enumerate_microstates(N):
        result[count_heads(state)] += 1
    return result

# Groups all generated microstates by their number of heads and counts each group.


def count_macrostate_multiplicities_fast(N: int) -> dict[int, int]:
    multiplicities = {}

    for k in range(N + 1):
        multiplicities[k] = 0

    for state in enumerate_microstates(N):
        k = state.bit_count()
        multiplicities[k] = multiplicities[k] + 1

    return multiplicities