"""Check entropy signs/units, parameter rounding and geometric waiting times."""
from fractions import Fraction
from math import comb, isclose, log, log10
import pytest
from src.thermodynamics import (K_B, macrostate_entropy, entropy_difference,
    harmonic_parameter, integer_system_size, log10_waiting_time)


def test_entropy_and_sign_convention():
    assert isclose(macrostate_entropy(7,3),K_B*log(35),rel_tol=1e-12)
    assert isclose(entropy_difference(7,1,2),K_B*log(1/3),rel_tol=1e-12)
    assert entropy_difference(100,75,50) < 0
    assert entropy_difference(100,60,50) < 0
    assert entropy_difference(100,50,20) > 0
    assert entropy_difference(7,3,3) == 0
    assert macrostate_entropy(7,0) == macrostate_entropy(7,7) == 0


def test_harmonic_mean_uses_reciprocals_and_exact_arithmetic():
    assert harmonic_parameter([10,20]) == Fraction(40,3)
    assert integer_system_size([10,20]) == (Fraction(40,3),113)
    assert integer_system_size([10,20],"ceil")[1] == 114
    assert integer_system_size([10,20],"floor")[1] == 113
    assert integer_system_size([71,71,71,71])[1] == 171


@pytest.mark.parametrize("digits", [[],[0,71],[-1],[100],[1,2,3,4,5],[True]])
def test_undefined_or_invalid_suffixes(digits):
    with pytest.raises(ValueError):
        harmonic_parameter(digits)


def test_waiting_time_rate_and_geometric_uncertainty():
    N,k=20,8
    expected=(1<<N)/comb(N,k)
    assert isclose(log10_waiting_time(N,k),log10(expected),rel_tol=1e-12)
    assert isclose(log10_waiting_time(N,k,2),log10(expected/2),rel_tol=1e-12)
    with pytest.raises(ValueError):
        log10_waiting_time(N,k,0)