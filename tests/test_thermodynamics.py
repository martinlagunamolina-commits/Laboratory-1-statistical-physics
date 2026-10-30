from math import log, isclose

import pytest

from src.thermodynamics import (
    macrostate_entropy,
    entropy_difference,
    K_B
)


def test_macrostate_entropy():
    N = 7
    k = 3

    expected = K_B * log(35)

    result = macrostate_entropy(N, k)

    assert isclose(result, expected, rel_tol=1e-12)


def test_entropy_difference():
    N = 7
    k1 = 1
    k2 = 2

    # Omega(7,1) = 7 and Omega(7,2) = 21
    expected = K_B * (log(7) - log(21))

    result = entropy_difference(N, k1, k2)

    assert isclose(result, expected, rel_tol=1e-12)


def test_entropy_difference_same_macrostate():
    # Comparing a macrostate with itself must give zero entropy difference.
    result = entropy_difference(7, 3, 3)

    assert isclose(result, 0.0, abs_tol=1e-30)


def test_entropy_symmetry():
    # Macrostates k and N-k have the same multiplicity.
    result1 = macrostate_entropy(10, 3)
    result2 = macrostate_entropy(10, 7)

    assert isclose(result1, result2, rel_tol=1e-12)


def test_invalid_macrostate():
    # The number of heads cannot exceed the number of coins.
    with pytest.raises(ValueError):
        macrostate_entropy(5, 7)