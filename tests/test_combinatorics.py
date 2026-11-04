from math import isclose, log, exp

from src.combinatorics import (
    multiplicity_count,
    multiplicity_gammaln,
    multiplicity_test,
    macrostate_probability_gammaln,
    macrostate_probability_count,
    macrostate_probability_test,
    multiplicities_by_recurrence,
    log_multiplicities_by_recurrence,
    log_multiplicity_gammaln
)
from src.microstates import count_macrostate_multiplicities


def test_multiplicity_test():
    assert multiplicity_test(7, 3) == 35
    assert multiplicity_test(5, 2) == 10



def test_multiplicity_count():
    for N in [3, 5, 8]:
        for k in range(N + 1):

            result = multiplicity_count(N, k)
            expected = multiplicity_test(N, k)

            assert isclose(
                result,
                expected,
                rel_tol=1e-12,
                abs_tol=1e-12
            )

def test_multiplicity_gammaln():
    for N in [5, 7, 20, 100]:
        for k in range(N + 1):

            result = multiplicity_gammaln(N, k)
            expected = multiplicity_test(N, k)

            assert isclose(
                result,
                expected,
                rel_tol=1e-12,
                abs_tol=1e-12
            )

def test_macrostatee_probability_test():
    assert(macrostate_probability_test(5,2))==0.3125
    assert(macrostate_probability_test(7,3))==0.2734375
    assert(macrostate_probability_test(10,4))==0.205078125

def test_macrostate_probability_gammaln():
    for N in [5, 7, 20, 100]:
            for k in range(N + 1):
                assert isclose(
                    macrostate_probability_gammaln(N, k),
                    macrostate_probability_test(N,k)
                )

def test_macrostate_probability_count():
    for N in [3, 5, 8]:
            for k in range(N + 1):
                assert isclose(
                    macrostate_probability_count(N, k),
                    macrostate_probability_test(N,k)
                )

def test_probabilities_sum_to_one_gammaln():
    N = 7

    total_probability = 0

    for k in range(N + 1):
        total_probability += macrostate_probability_gammaln(N, k)

    assert isclose(total_probability, 1.0)

def test_probabilities_sum_to_one_count():
    N = 7

    total_probability = 0

    for k in range(N + 1):
        total_probability += macrostate_probability_count(N, k)

    assert isclose(total_probability, 1.0) 


def test_multiplicities_by_recurrence():
    expected = {
        0: 1,
        1: 5,
        2: 10,
        3: 10,
        4: 5,
        5: 1
    }

    assert multiplicities_by_recurrence(5) == expected


def test_recurrence_matches_enumeration():
    for N in range(9):
        original = count_macrostate_multiplicities(N)
        optimized = multiplicities_by_recurrence(N)

        assert optimized == original


def test_recurrence_sum():
    for N in range(20):
        multiplicities = multiplicities_by_recurrence(N)

        assert sum(multiplicities.values()) == 2**N


def test_recurrence_symmetry():
    N = 10
    multiplicities = multiplicities_by_recurrence(N)

    for k in range(N + 1):
        assert multiplicities[k] == multiplicities[N - k]


def test_log_recurrence_matches_gammaln():
    for N in [0, 1, 2, 5, 20, 100]:
        log_values = log_multiplicities_by_recurrence(N)

        for k in range(N + 1):
            expected = log_multiplicity_gammaln(N, k)

            assert isclose(
                log_values[k],
                expected,
                rel_tol=1e-12,
                abs_tol=1e-12
            )


def test_log_recurrence_symmetry():
    N = 20
    log_values = log_multiplicities_by_recurrence(N)

    for k in range(N + 1):
        assert log_values[k] == log_values[N - k]

