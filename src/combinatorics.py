from scipy.special import gammaln
from src.microstates import count_macrostate_multiplicities
from math import comb, log, exp

def multiplicity_count(N: int, k: int) -> int:

    multiplicities = count_macrostate_multiplicities(N)

    return multiplicities[k] 

def multiplicity_gammaln(N: int, k: int) -> float:

    if N < 0 or k < 0 or k > N:
        raise ValueError("Invalid values of N and k.")

    log_omega = (
        gammaln(N + 1)
        - gammaln(k + 1)
        - gammaln(N - k + 1)
    )

    omega = exp(log_omega)

    return omega


def log_multiplicity_gammaln(N: int, k: int) -> float:

    if N < 0 or k < 0 or k > N:
        raise ValueError("Invalid values of N and k.")

    log_omega = (
        gammaln(N + 1)
        - gammaln(k + 1)
        - gammaln(N - k + 1)
    )

    return log_omega
#We output here log_omega, instead of omega, for further probability calculations in lof space, and for entropy calculations.



def multiplicity_test(N: int, k: int) -> int:
        
    if N < 0 or k < 0 or k > N:
        raise ValueError("Invalid values of N and k.")

    return comb(N, k)
#Calculate the exact multiplicity using the binomial coefficient. Only for verification.


def multiplicities_by_recurrence(N: int) -> dict[int, int]:
    multiplicities = {0: 1}
    omega = 1

    for k in range(N):
        omega = omega * (N - k) // (k + 1)
        multiplicities[k + 1] = omega

    return multiplicities

#Computes all multiplicities for 0<k<=N

def log_multiplicities_by_recurrence(N: int) -> dict[int, float]:
    log_multiplicities = {0: 0.0}
    log_omega = 0.0

    # Calculate the values up to the middle of the distribution.
    for k in range(N // 2):
        log_omega = log_omega + log(N - k) - log(k + 1)
        log_multiplicities[k + 1] = log_omega

    # Use the symmetry Omega(N,k) = Omega(N,N-k).
    for k in range(N // 2 + 1, N + 1):
        log_multiplicities[k] = log_multiplicities[N - k]

    return log_multiplicities

#Computes all multiplicities for 0<k<=N in log




def macrostate_probability_count(N: int, k: int) -> float:

    omega = multiplicity_count(N, k)
    total = 1 << N

    return omega / total



def macrostate_probability_gammaln(N: int, k: int) -> float:

    log_omega = log_multiplicity_gammaln(N, k)

    log_probability = log_omega - N * log(2)

    return exp(log_probability)

#We do it in log space to avoid numerical problems


def macrostate_probability_test(N: int, k: int) -> float:

    omega = multiplicity_test(N, k)
    total = 1 << N

    return omega / total