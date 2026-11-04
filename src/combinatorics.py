"""Exact recurrence, log-gamma multiplicities and stable binomial probabilities."""

from math import comb, exp, log
import numpy as np
from scipy.special import gammaln, logsumexp
from src.microstates import count_macrostate_multiplicities, validate_n


def validate_macrostate(N: int, k: int) -> None:
    """Check that k is an integer heads count in [0, N]."""
    validate_n(N)
    if isinstance(k, bool) or not isinstance(k, int) or not 0 <= k <= N:
        raise ValueError("k must be an integer between 0 and N.")


def exact_multiplicities(N: int) -> list[int]:
    """Return all coefficients by Omega(k+1)=Omega(k)*(N-k)//(k+1)."""
    validate_n(N)
    values = [1]
    for k in range(N):
        values.append(values[-1] * (N - k) // (k + 1))
    return values


def multiplicity_count(N: int, k: int) -> int:
    """Return multiplicity by explicit enumeration; intended only for small N."""
    validate_macrostate(N, k)
    return count_macrostate_multiplicities(N)[k]


def log_multiplicity_gammaln(N: int, k: int) -> float:
    """Return ln(Omega) with log-gamma; use only for numerically moderate N.

    At N~1e23 cancellation and integer-to-float rounding destroy accuracy;
    the report uses asymptotic formulas instead of this function there.
    """
    validate_macrostate(N, k)
    if k in (0, N):
        return 0.0
    return float(gammaln(N + 1) - gammaln(k + 1) - gammaln(N - k + 1))


def multiplicity_gammaln(N: int, k: int) -> float:
    """Exponentiate ln(Omega); may overflow, so prefer the log function."""
    return exp(log_multiplicity_gammaln(N, k))


def multiplicity_test(N: int, k: int) -> int:
    """Independent exact library reference used for verification only."""
    validate_macrostate(N, k)
    return comb(N, k)


def log_probability(N: int, k: int) -> float:
    """Return ln(P(K=k)); a logarithm can represent extremely rare events."""
    return log_multiplicity_gammaln(N, k) - N * log(2.0)


def macrostate_probability_gammaln(N: int, k: int) -> float:
    """Return P(K=k); very small results can underflow to zero."""
    return exp(log_probability(N, k))


def macrostate_probability_count(N: int, k: int) -> float:
    """Evaluate a probability through explicit small-system enumeration."""
    return multiplicity_count(N, k) / (1 << N)


def macrostate_probability_test(N: int, k: int) -> float:
    """Exact-integer reference before conversion to a floating probability."""
    return multiplicity_test(N, k) / (1 << N)


def cumulative_probability(N: int, lower: int, upper: int) -> float:
    """Sum the inclusive integer interval; an empty interval has probability 0."""
    validate_macrostate(N, lower)
    validate_macrostate(N, upper)
    if lower > upper:
        return 0.0
    return float(exp(logsumexp([log_probability(N, k) for k in range(lower, upper + 1)])))


def log_distribution(N: int) -> tuple[np.ndarray, np.ndarray]:
    """Return all integer k and ln(Omega) as float64 arrays; O(N) memory.

    Masking endpoints enforces their exact zero logarithm. Do not use for
    macroscopic N: full-grid allocation and cancellation impose limits.
    """
    validate_n(N)
    k = np.arange(N + 1, dtype=np.float64)
    values = gammaln(N + 1) - gammaln(k + 1) - gammaln(N - k + 1)
    values[0] = values[-1] = 0.0
    return k, values