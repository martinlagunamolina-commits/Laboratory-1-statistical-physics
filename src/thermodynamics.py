"""Boltzmann entropy, harmonic-mean parameters and independent-trial waiting times."""

from fractions import Fraction
from math import ceil, floor, log, log10
from src.combinatorics import log_multiplicity_gammaln, log_probability

K_B = 1.380649e-23  # J K^-1; exact SI definition


def harmonic_parameter(digits: list[int]) -> Fraction:
    """Return exact harmonic mean of 1..4 positive two-digit NIA suffixes.

    Suffix 00 is rejected: the literal reciprocal definition is undefined.
    An instructor must specify a convention for that case.
    """
    if not 1 <= len(digits) <= 4 or any(
        isinstance(d, bool) or not isinstance(d, int) or not 1 <= d <= 99 for d in digits
    ):
        raise ValueError("Supply 1..4 integer NIA suffixes in 1..99; 00 needs clarification.")
    return Fraction(len(digits), 1) / sum((Fraction(1, d) for d in digits), Fraction(0))


def integer_system_size(digits: list[int], rounding: str = "nearest") -> tuple[Fraction, int]:
    """Return exact M and integer N; nearest means half-up, not bankers' rounding.

    The manual does not prescribe rounding. This is an explicit provisional
    convention; --rounding floor/ceil allows the instructor's chosen rule.
    """
    M = harmonic_parameter(digits)
    if rounding == "nearest":
        offset = floor(M + Fraction(1, 2))
    elif rounding == "floor":
        offset = floor(M)
    elif rounding == "ceil":
        offset = ceil(M)
    else:
        raise ValueError("Unknown rounding convention.")
    return M, 100 + offset


def macrostate_entropy(N: int, k: int) -> float:
    """Return Boltzmann macrostate entropy in J/K (natural logarithm)."""
    return K_B * log_multiplicity_gammaln(N, k)


def entropy_difference(N: int, k1: int, k2: int) -> float:
    """Return S(k1)-S(k2) in J/K, following the manual's sign convention."""
    return K_B * (log_multiplicity_gammaln(N, k1) - log_multiplicity_gammaln(N, k2))


def log10_waiting_time(N: int, k: int, trials_per_second: float = 1.0) -> float:
    """Return log10(mean seconds) for independent, complete-system trials.

    N individual coins/second means one complete N-coin trial/second.
    Sequential single-coin updates are correlated and need another model.
    """
    if trials_per_second <= 0:
        raise ValueError("Trial rate must be positive.")
    return -log_probability(N, k) / log(10.0) - log10(trials_per_second)