from src.combinatorics import log_multiplicity_gammaln


# Boltzmann constant in J/K
K_B = 1.380649e-23


def macrostate_entropy(N: int, k: int) -> float:

    entropy = K_B * log_multiplicity_gammaln(N,k)

    return entropy


def entropy_difference(N: int, k1: int, k2: int) -> float:

    entropy_1 = macrostate_entropy(N, k1)
    entropy_2 = macrostate_entropy(N, k2)

    delta_S = entropy_1 - entropy_2

    return delta_S