from scipy.special import gammaln
import math
from src.microstates import count_macrostate_multiplicities
from math import comb

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

    omega = math.exp(log_omega)

    return omega

def multiplicity_test(N: int, k: int) -> int:
        
    if N < 0 or k < 0 or k > N:
        raise ValueError("Invalid values of N and k.")

    return comb(N, k)
#Calculate the exact multiplicity using the binomial coefficient. Only for verification.