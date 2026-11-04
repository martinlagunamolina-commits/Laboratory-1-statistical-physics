"""Exhaustive small-system checks for integer encodings and macrostate counts."""
import pytest
from math import comb
from src.microstates import (total_microstates, enumerate_microstates, count_heads,
                             count_macrostate_multiplicities, state_string)


@pytest.mark.parametrize("N", range(9))
def test_complete_unique_enumeration(N):
    states = list(enumerate_microstates(N))
    assert states == list(range(2**N))
    assert len(set(states)) == total_microstates(N)
    assert count_macrostate_multiplicities(N) == {k: comb(N,k) for k in range(N+1)}


def test_seven_coin_listing_has_all_states():
    strings = [state_string(s,7) for s in enumerate_microstates(7)]
    assert len(strings) == len(set(strings)) == 128
    for s, text in enumerate(strings):
        assert len(text) == 7
        assert text.count("H") == count_heads(s) == s.bit_count()
    assert state_string(0,0) == ""


@pytest.mark.parametrize("value", [-1, 2.5, True, "7"])
def test_invalid_inputs(value):
    with pytest.raises(ValueError):
        total_microstates(value)
    with pytest.raises(ValueError):
        list(enumerate_microstates(value))
    with pytest.raises(ValueError):
        count_heads(value)


def test_state_must_fit_width():
    with pytest.raises(ValueError):
        state_string(8,3)