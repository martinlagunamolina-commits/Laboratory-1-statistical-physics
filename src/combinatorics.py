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