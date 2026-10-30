from math import isclose, log, exp

from src.combinatorics import (
    multiplicity_count,
    multiplicity_gammaln,
    multiplicity_test,
    macrostate_probability_gammaln,
    macrostate_probability_count,
    macrostate_probability_test
)


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