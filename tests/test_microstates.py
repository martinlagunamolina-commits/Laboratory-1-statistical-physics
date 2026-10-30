from src.microstates import (
    total_microstates,
    enumerate_microstates,
    count_heads,
    count_macrostate_multiplicities
)


def test_total_microstates():
    assert total_microstates(0) == 1
    assert total_microstates(1) == 2
    assert total_microstates(3) == 8
    assert total_microstates(5) == 32


def test_enumerate_microstates():
    states = list(enumerate_microstates(3))

    assert len(states) == 8
    assert states == list(range(8))
    assert len(set(states)) == 8


def test_count_heads():
    assert count_heads(0) == 0
    assert count_heads(1) == 1
    assert count_heads(5) == 2
    assert count_heads(7) == 3


def test_macrostate_multiplicities():
    result = count_macrostate_multiplicities(3)

    assert result == {
        0: 1,
        1: 3,
        2: 3,
        3: 1
    }