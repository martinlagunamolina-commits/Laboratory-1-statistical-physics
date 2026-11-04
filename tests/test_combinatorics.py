"""Independent exact references and distribution invariants."""
from math import comb, isclose, log
import numpy as np
import pytest
from src.combinatorics import (exact_multiplicities, log_multiplicity_gammaln,
    multiplicity_count, multiplicity_gammaln, macrostate_probability_gammaln,
    macrostate_probability_count, macrostate_probability_test,
    cumulative_probability, log_probability, log_distribution)


@pytest.mark.parametrize("N", [0,1,7,20,50,80,100,199])
def test_recurrence_exact_coefficients_and_binomial_theorem(N):
    values = exact_multiplicities(N)
    assert values == [comb(N,k) for k in range(N+1)]
    assert sum(values) == 1 << N
    assert values == values[::-1]


@pytest.mark.parametrize("N", [7,100,199,1000,10000])
def test_log_gamma_against_exact_integers(N):
    for k in {0,1, N//4, N//2, N-1,N}:
        assert abs(log_multiplicity_gammaln(N,k)-log(comb(N,k))) < 1e-9


def test_all_original_computational_routes_agree():
    for N in range(9):
        for k in range(N+1):
            exact = comb(N,k)
            assert multiplicity_count(N,k) == exact
            assert isclose(multiplicity_gammaln(N,k),exact,rel_tol=2e-12)
            expected = exact/(1<<N)
            for fn in [macrostate_probability_gammaln,macrostate_probability_count,macrostate_probability_test]:
                assert isclose(fn(N,k),expected,rel_tol=2e-12)


@pytest.mark.parametrize("N", [20,50,80,100,199,10000])
def test_probability_normalization_symmetry_and_mean(N):
    k, logs = log_distribution(N)
    p = np.exp(logs-N*log(2))
    assert abs(p.sum()-1) < 1e-9
    assert np.max(abs(p-p[::-1])) < 1e-10
    assert abs((k*p).sum()-N/2) < 1e-5
    assert abs((((k-N/2)**2)*p).sum()-N/4) < 1e-5


def test_inclusive_intervals_and_tails_symmetry():
    N=151
    low,high=66,85
    exact=sum(comb(N,k) for k in range(low,high+1))/(1<<N)
    assert isclose(cumulative_probability(N,low,high),exact,rel_tol=1e-11)
    assert isclose(cumulative_probability(N,low,high),cumulative_probability(N,N-high,N-low),rel_tol=1e-11)
    assert cumulative_probability(N,3,2) == 0
    assert isclose(cumulative_probability(N,30,30),macrostate_probability_gammaln(N,30))


def test_log_probability_survives_probability_underflow():
    assert log_probability(10000,0) < -6000
    assert macrostate_probability_gammaln(10000,0) == 0.0


@pytest.mark.parametrize("N,k", [(-1,0),(4,-1),(4,5),(4,1.2),(True,0)])
def test_invalid_macrostates(N,k):
    with pytest.raises(ValueError):
        log_multiplicity_gammaln(N,k)
