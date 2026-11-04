"""Main program for Sections 1 and 2 of Statistical Physics Lab 1."""

import csv
import math
import time
import shutil
import subprocess
import sys
from pathlib import Path
from decimal import Decimal, localcontext

# Always use the folder containing main.py as the project root. This allows
# the program to be launched from VS Code or from a terminal in another folder.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# The src package is part of the project and provides the existing calculations.
if not (PROJECT_ROOT / "src" / "__init__.py").is_file():
    raise SystemExit(
        "Could not find the project src/ folder.\n"
        "Place main.py in the project root, next to the src/ folder.\n"
        "Do not run a standalone copy of main.py without the project files."
    )

import matplotlib.pyplot as plt

from src.microstates import enumerate_microstates, count_heads_fast
from src.combinatorics import (
    multiplicities_by_recurrence,
    log_multiplicities_by_recurrence,
    log_multiplicity_gammaln,
    macrostate_probability_gammaln,
)
from src.thermodynamics import macrostate_entropy, entropy_difference
from src.benchmark import run_five_minute_challenge


# ---------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------

RESULTS_FOLDER = PROJECT_ROOT / "results"
FIGURES_FOLDER = PROJECT_ROOT / "report" / "figures"
REPORT_FOLDER = PROJECT_ROOT / "report"

# Values required in Task 1c.
N_VALUES = [20, 50, 80, 100]

# Values to investigate in Task 1d.
# These are test values, not a maximum imposed by the teacher.
DISTRIBUTION_TEST_VALUES = [100, 500, 1000, 2000, 5000, 10000,
                            20000, 50000, 100000]

# Keep these False during normal runs because the benchmarks can take time.
RUN_ENUMERATION_BENCHMARK = False
RUN_DISTRIBUTION_TEST = False

# Compile report/main.tex automatically after all calculations and plots finish.
# Set this to False if LaTeX is not installed or you do not want automatic compilation.
COMPILE_LATEX_REPORT = True

# Team-specific value: M = 31.2066, so N = round(100 + M) = 131.
# ASSUMPTION: for odd N, use the nearest integer to N/2 + offset,
# rounding half-integers upward. Confirm this convention with your professor.
TEAM_N = 131


# ---------------------------------------------------------
# TASK 1a: ENUMERATE ALL MICROSTATES FOR N = 7
# ---------------------------------------------------------

def enumerate_seven_coins():
    """List all 128 microstates for seven coins, grouped by number of heads."""

    N = 7

    # Create eight empty lists: one list for each possible number of heads.
    groups = {}
    for k in range(N + 1):
        groups[k] = []

    # Generate every microstate and put it in its correct group.
    for state in enumerate_microstates(N):
        number_of_heads = count_heads_fast(state)

        # Convert the integer into seven binary digits, then H and T.
        binary = format(state, "07b")
        coin_string = binary.replace("0", "T").replace("1", "H")

        groups[number_of_heads].append(coin_string)

    # Check our result against the binomial recurrence.
    expected = multiplicities_by_recurrence(N)

    for k in range(N + 1):
        if len(groups[k]) != expected[k]:
            raise ValueError("The N=7 enumeration is not correct.")

    # Save all 128 microstates in a text file.
    RESULTS_FOLDER.mkdir(exist_ok=True)
    output_file = RESULTS_FOLDER / "microstates_N7.txt"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write("All microstates for N = 7\n\n")

        for k in range(N + 1):
            file.write(f"{k} heads and {N-k} tails: {len(groups[k])} microstates\n")

            for state in groups[k]:
                file.write(state + "\n")

            file.write("\n")

    print("Task 1a finished.")
    print("Multiplicities for k = 0,...,7:", [len(groups[k]) for k in range(N + 1)])
    print("All microstates saved in:", output_file)


# ---------------------------------------------------------
# TASK 1b: FIVE-MINUTE FULL-ENUMERATION BENCHMARK
# ---------------------------------------------------------

def run_enumeration_benchmark():
    """Find the largest N that can be fully enumerated within five minutes."""

    RESULTS_FOLDER.mkdir(exist_ok=True)

    results = run_five_minute_challenge(
        output_csv=RESULTS_FOLDER / "enumeration_benchmark.csv"
    )

    # Save a short summary of the benchmark.
    summary_file = RESULTS_FOLDER / "enumeration_benchmark_summary.txt"

    with open(summary_file, "w", encoding="utf-8") as file:
        file.write(f"Original method: maximum N = {results['original_max_N']}\n")
        file.write(f"Optimized method: maximum N = {results['optimized_max_N']}\n")
        file.write("Time limit: 300 seconds for each tested N.\n")

    print("Task 1b finished.")
    print("Benchmark summary saved in:", summary_file)


# ---------------------------------------------------------
# TASK 1c: DISTRIBUTIONS FOR N = 20, 50, 80 AND 100
# ---------------------------------------------------------

def make_distribution_plots():
    """Calculate the multiplicities and save one combined and four individual plots."""

    RESULTS_FOLDER.mkdir(exist_ok=True)
    FIGURES_FOLDER.mkdir(parents=True, exist_ok=True)

    csv_file = RESULTS_FOLDER / "macrostate_distributions.csv"

    # This figure compares all four distributions in one plot.
    combined_figure, combined_axes = plt.subplots()

    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["N", "k", "multiplicity"])

        for N in N_VALUES:
            # Calculate Omega(N,k) for every k.
            multiplicities = multiplicities_by_recurrence(N)

            # Check that the multiplicities add up to 2^N.
            if sum(multiplicities.values()) != 2**N:
                raise ValueError(f"Incorrect multiplicities for N={N}.")

            k_values = list(range(N + 1))
            omega_values = [multiplicities[k] for k in k_values]

            # Save the numerical values in the CSV file.
            for k in k_values:
                writer.writerow([N, k, multiplicities[k]])

            # Add this distribution to the combined plot.
            combined_axes.plot(k_values, omega_values, label=f"N = {N}")

            # Save an individual plot with a linear vertical axis.
            figure, axes = plt.subplots()
            axes.plot(k_values, omega_values)
            axes.set_xlabel("Number of heads, k")
            axes.set_ylabel(r"Multiplicity, $\Omega(N,k)$")
            axes.set_title(f"Macrostate distribution for N = {N}")
            axes.grid(True)
            figure.savefig(FIGURES_FOLDER / f"distribution_N{N}.pdf")
            plt.close(figure)

    # The multiplicities are very different in size, so use a log scale
    # for the combined plot to make all four curves visible.
    combined_axes.set_yscale("log")
    combined_axes.set_xlabel("Number of heads, k")
    combined_axes.set_ylabel(r"Multiplicity, $\Omega(N,k)$")
    combined_axes.set_title("Macrostate distributions for different N")
    combined_axes.legend()
    combined_axes.grid(True, which="both")
    combined_figure.savefig(FIGURES_FOLDER / "all_distributions.pdf")
    plt.close(combined_figure)

    print("Task 1c finished.")
    print("Numerical values saved in:", csv_file)
    print("Combined plot saved in:", FIGURES_FOLDER / "all_distributions.pdf")
    print("Individual plots saved in:", FIGURES_FOLDER)


# ---------------------------------------------------------
# TASK 1d: HOW LARGE A DISTRIBUTION CAN WE CALCULATE AND PLOT?
# ---------------------------------------------------------

def test_distribution_sizes():
    """Measure calculation and plotting times for increasingly large N values."""

    RESULTS_FOLDER.mkdir(exist_ok=True)
    FIGURES_FOLDER.mkdir(parents=True, exist_ok=True)

    csv_file = RESULTS_FOLDER / "distribution_scaling.csv"
    final_figure = FIGURES_FOLDER / "distribution_scaling_test.pdf"

    largest_N_completed = None

    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["N", "calculation_seconds", "plotting_seconds", "total_seconds"])

        # Try each N in the list above, from smallest to largest.
        for N in DISTRIBUTION_TEST_VALUES:
            print(f"Testing distribution calculation and plot for N = {N}...")

            # First, calculate log(Omega) for all k.
            start_time = time.perf_counter()
            log_multiplicities = log_multiplicities_by_recurrence(N)
            calculation_time = time.perf_counter() - start_time

            # Check that we have one value for every k = 0,...,N.
            if len(log_multiplicities) != N + 1:
                raise ValueError(f"Incorrect number of macrostates for N={N}.")

            # Convert natural logarithms into log base 10 for the plot.
            k_values = list(range(N + 1))
            log10_values = [
                log_multiplicities[k] / math.log(10)
                for k in k_values
            ]

            # Now measure how long it takes to create and save the PDF plot.
            start_time = time.perf_counter()

            figure, axes = plt.subplots()
            axes.plot(k_values, log10_values)
            axes.set_xlabel("Number of heads, k")
            axes.set_ylabel(r"$\log_{10}\Omega(N,k)$")
            axes.set_title(f"Distribution for N = {N}")
            axes.grid(True)
            figure.savefig(final_figure)
            plt.close(figure)

            plotting_time = time.perf_counter() - start_time
            total_time = calculation_time + plotting_time

            # Save the measured times.
            writer.writerow([
                N,
                f"{calculation_time:.6f}",
                f"{plotting_time:.6f}",
                f"{total_time:.6f}"
            ])
            file.flush()

            print(
                f"  Calculation: {calculation_time:.3f} s; "
                f"plotting: {plotting_time:.3f} s; "
                f"total: {total_time:.3f} s"
            )

            largest_N_completed = N

    # This is the largest value in our chosen test list that completed.
    summary_file = RESULTS_FOLDER / "distribution_scaling_summary.txt"

    with open(summary_file, "w", encoding="utf-8") as file:
        file.write("TASK 1d: DISTRIBUTION CALCULATION AND PLOTTING\n\n")
        file.write(f"Largest tested N completed: {largest_N_completed}\n")
        file.write("The method calculates log multiplicities using a recurrence.\n")
        file.write("The plot shows log10(Omega) against the number of heads k.\n")
        file.write("The reported maximum is the largest tested value, not a universal limit.\n")
        file.write("The practical limit depends on the computer and the chosen candidate values.\n")

    print("Task 1d finished.")
    print("Measurements saved in:", csv_file)
    print("Summary saved in:", summary_file)
    print("Plot for the largest tested N saved in:", final_figure)
    print("Largest tested N completed:", largest_N_completed)


# ---------------------------------------------------------
# TASK 1e: NUMERICAL ILLUSTRATION OF THE THERMODYNAMIC LIMIT
# ---------------------------------------------------------

def show_thermodynamic_limit():
    """Calculate the mean, standard deviation and relative fluctuation for N=10^23."""

    N = 10**23

    # For unbiased coins, the mean number of heads is N/2.
    mean_heads = N / 2

    # The standard deviation is sqrt(N)/2.
    standard_deviation = math.sqrt(N) / 2

    # Relative fluctuations tell us how large the fluctuations are
    # compared with the average number of heads.
    relative_fluctuation = standard_deviation / mean_heads

    RESULTS_FOLDER.mkdir(exist_ok=True)
    output_file = RESULTS_FOLDER / "thermodynamic_limit.txt"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write("THERMODYNAMIC LIMIT: N = 10^23\n\n")
        file.write(f"Number of coins: N = {N:.1e}\n")
        file.write(f"Mean number of heads: {mean_heads:.6e}\n")
        file.write(f"Standard deviation: {standard_deviation:.6e}\n")
        file.write(f"Relative fluctuation: {relative_fluctuation:.6e}\n")

    print("\nTASK 1e: THERMODYNAMIC LIMIT")
    print("Mean number of heads:", f"{mean_heads:.6e}")
    print("Standard deviation:", f"{standard_deviation:.6e}")
    print("Relative fluctuation:", f"{relative_fluctuation:.6e}")
    print("Numerical results saved in:", output_file)



# ---------------------------------------------------------
# SECTION 2: PROBABILITIES, ENTROPY AND THERMODYNAMICS
# ---------------------------------------------------------

def run_section_2():
    """Calculate the numerical answers requested in Section 2."""

    N = TEAM_N

    # N=131 is odd, so the two most probable macrostates are k=65 and k=66.
    # We use k=66 as the central macrostate. They have equal probability.
    middle = (N + 1) // 2

    # The assignment uses N/2 plus or minus offsets. For odd N, we round
    # half-integer values to the nearest integer, with .5 rounded upward.
    k_plus_10 = middle + 10
    k_plus_25 = middle + 25

    # a) Probability of exactly 30 heads.
    probability_30 = macrostate_probability_gammaln(N, 30)

    # b) Probability of one of the two most probable macrostates.
    probability_middle = macrostate_probability_gammaln(N, middle)

    # c) Probability of being within 10 heads of N/2.
    # Keep only integer k values whose distance from N/2 is at most 10.
    lower_10 = math.ceil(N / 2 - 10)
    upper_10 = math.floor(N / 2 + 10)
    cumulative_10 = sum(
        macrostate_probability_gammaln(N, k)
        for k in range(lower_10, upper_10 + 1)
    )

    # d) Probability of being within 20 heads of N/2.
    lower_20 = math.ceil(N / 2 - 20)
    upper_20 = math.floor(N / 2 + 20)
    cumulative_20 = sum(
        macrostate_probability_gammaln(N, k)
        for k in range(lower_20, upper_20 + 1)
    )

    # e), f), g) Entropy differences: Delta S = S(k1) - S(k2).
    delta_s_25 = entropy_difference(N, k_plus_25, middle)
    delta_s_10 = entropy_difference(N, k_plus_10, middle)
    delta_s_20 = entropy_difference(N, middle, 20)

    # h) One complete configuration is produced each second because the
    # tossing rate is N coins/second. Mean waiting time = 1 / P(k=8).
    probability_8 = macrostate_probability_gammaln(N, 8)
    waiting_time = 1 / probability_8

    # i) Likelihood ratio: central macrostate / macrostate N/2 + 10.
    # Calculate it in log-space to avoid numerical overflow.
    log_ratio = (
        log_multiplicity_gammaln(N, middle)
        - log_multiplicity_gammaln(N, k_plus_10)
    )
    likelihood_ratio = math.exp(log_ratio)

    # Save all numerical answers in a readable text file.
    RESULTS_FOLDER.mkdir(exist_ok=True)
    output_file = RESULTS_FOLDER / "section2_results.txt"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write("SECTION 2: PROBABILITIES, ENTROPY AND THERMODYNAMICS\n")
        file.write(f"Team value: N = {N}\n")
        file.write(f"Chosen central macrostate: k = {middle}\n")
        file.write("Convention: nearest integer, half-integers rounded upward.\n\n")
        file.write(f"a) P(k=30) = {probability_30:.12e}\n")
        file.write(f"b) P(k={middle}) = {probability_middle:.12e}\n")
        file.write(f"c) P({lower_10} <= k <= {upper_10}) = {cumulative_10:.12e}\n")
        file.write(f"d) P({lower_20} <= k <= {upper_20}) = {cumulative_20:.12e}\n")
        file.write(f"e) Delta S = S({k_plus_25}) - S({middle}) = {delta_s_25:.12e} J/K\n")
        file.write(f"f) Delta S = S({k_plus_10}) - S({middle}) = {delta_s_10:.12e} J/K\n")
        file.write(f"g) Delta S = S({middle}) - S(20) = {delta_s_20:.12e} J/K\n")
        file.write(f"h) P(k=8) = {probability_8:.12e}\n")
        file.write(f"   Expected waiting time = {waiting_time:.12e} seconds\n")
        file.write(f"i) Likelihood ratio = {likelihood_ratio:.12e}\n")
        file.write(f"   Compared macrostates: k={middle} and k={k_plus_10}\n")

    print("\nSECTION 2 FINISHED")
    print("N =", N)
    print("Results saved in:", output_file)
    print("Probability P(k=30):", probability_30)
    print("Probability of central macrostate:", probability_middle)
    print("Cumulative probability (+/- 10):", cumulative_10)
    print("Cumulative probability (+/- 20):", cumulative_20)
    print("Expected waiting time for 8 heads (s):", waiting_time)
    print("Likelihood ratio:", likelihood_ratio)


# ---------------------------------------------------------
# SECTION 2k: REPEAT SECTION 2 FOR A MACROSCOPIC SYSTEM
# ---------------------------------------------------------

def run_large_n_section_2():
    """Re-evaluate Section 2 for N = 10^23 using analytical approximations.

    Direct enumeration is impossible for this N. We use Stirling's
    approximation and large-N binomial formulas instead. Decimal arithmetic
    keeps the very large logarithms and very small corrections readable.
    """

    N = 10**23
    k_B = Decimal("1.380649e-23")
    pi = Decimal("3.14159265358979323846264338327950288419716939937510")

    # Use extra precision because some results are extremely large or small.
    with localcontext() as context:
        context.prec = 60

        N_decimal = Decimal(N)
        ln_2 = Decimal(2).ln()
        ln_10 = Decimal(10).ln()
        ln_N = N_decimal.ln()

        # A small helper for probabilities with a fixed number of heads.
        # It uses the exact binomial expression in logarithmic form:
        # C(N,k) = N**k/k! * product(1-j/N), for j=0,...,k-1.
        def log_binomial_fixed_k(k):
            log_value = (
                Decimal(k) * ln_N
                - Decimal(math.factorial(k)).ln()
            )
            for j in range(k):
                log_value += (Decimal(1) - Decimal(j) / N_decimal).ln()
            return log_value

        # -----------------------------------------------------
        # a) Probability of exactly 30 heads.
        # We calculate log10(P) because the probability is too small
        # to represent as an ordinary floating-point number.
        # -----------------------------------------------------
        k_a = 30
        log10_probability_30 = (
            log_binomial_fixed_k(k_a) - N_decimal * ln_2
        ) / ln_10

        # -----------------------------------------------------
        # b) Probability of the central macrostate, k = N/2.
        # Stirling's approximation gives:
        # P(N/2) approximately sqrt(2 / (pi*N)).
        # -----------------------------------------------------
        half_N = N_decimal / Decimal(2)
        probability_central = (Decimal(2) / (pi * N_decimal)).sqrt()

        # Calculate the probability of a symmetric window around N/2.
        # The probability at N/2+j divided by the central probability is
        # the product of (N/2-r+1)/(N/2+r), for r=1,...,j.
        def probability_within(offset):
            relative_probability = Decimal(1)
            total_relative_probability = Decimal(1)

            for j in range(1, offset + 1):
                relative_probability *= (
                    (half_N - Decimal(j) + Decimal(1))
                    / (half_N + Decimal(j))
                )
                # The +j and -j macrostates have equal probability.
                total_relative_probability += Decimal(2) * relative_probability

            return probability_central * total_relative_probability

        # -----------------------------------------------------
        # c) Probability from N/2 - 10 to N/2 + 10.
        # -----------------------------------------------------
        probability_within_10 = probability_within(10)

        # -----------------------------------------------------
        # d) Probability from N/2 - 20 to N/2 + 20.
        # -----------------------------------------------------
        probability_within_20 = probability_within(20)

        # Calculate the exact logarithm of the multiplicity ratio between
        # a macrostate N/2+m and the central macrostate.
        def log_offset_over_central(offset):
            log_ratio = Decimal(0)
            for j in range(1, offset + 1):
                one_step_ratio = (
                    Decimal(1)
                    - Decimal(2 * j - 1) / (half_N + Decimal(j))
                )
                log_ratio += one_step_ratio.ln()
            return log_ratio

        # -----------------------------------------------------
        # e) and f) Entropy differences, Delta S = k_B * ln(Omega1/Omega2).
        # -----------------------------------------------------
        delta_s_25 = k_B * log_offset_over_central(25)
        delta_s_10 = k_B * log_offset_over_central(10)

        # -----------------------------------------------------
        # g) Entropy difference between N/2 and k=20.
        # Stirling's approximation:
        # ln C(N,N/2) approximately N ln(2) - 1/2 ln(pi*N/2).
        # The k=20 multiplicity is evaluated with the fixed-k expression.
        # -----------------------------------------------------
        log_omega_central = (
            N_decimal * ln_2
            - Decimal("0.5") * (pi * N_decimal / Decimal(2)).ln()
        )
        log_omega_20 = log_binomial_fixed_k(20)
        delta_s_central_vs_20 = k_B * (log_omega_central - log_omega_20)

        # -----------------------------------------------------
        # h) Expected waiting time for exactly 8 heads.
        # One complete N-coin toss is made each second, so t_mean = 1/P_8.
        # We report log10(t_mean) because the waiting time is enormous.
        # -----------------------------------------------------
        k_h = 8
        log10_probability_8 = (
            log_binomial_fixed_k(k_h) - N_decimal * ln_2
        ) / ln_10
        log10_waiting_time = -log10_probability_8

        # -----------------------------------------------------
        # i) Likelihood ratio: central macrostate / macrostate N/2 + 10.
        # The ratio is so close to 1 that ordinary floats round it to 1.
        # Decimal arithmetic lets us show the tiny excess over 1.
        # -----------------------------------------------------
        log_likelihood_ratio = -log_offset_over_central(10)
        likelihood_ratio_excess = log_likelihood_ratio.exp() - Decimal(1)

        # Save the results and the approximations used.
        RESULTS_FOLDER.mkdir(exist_ok=True)
        output_file = RESULTS_FOLDER / "section2_large_N_results.txt"

        with open(output_file, "w", encoding="utf-8") as file:
            file.write("SECTION 2k: LARGE-N LIMIT\n")
            file.write("N = 10^23 unbiased coins\n")
            file.write("Analytical approximations are used; no enumeration is performed.\n\n")

            file.write("a) Probability of exactly 30 heads\n")
            file.write("   log10(P(k=30)) = " + str(log10_probability_30) + "\n")
            file.write("   P(k=30) is approximately 10 raised to this exponent.\n\n")

            file.write("b) Probability of the central macrostate\n")
            file.write("   P(k=N/2) approximately sqrt(2/(pi*N))\n")
            file.write("   P(k=N/2) = " + format(probability_central, ".12E") + "\n\n")

            file.write("c) Cumulative probability within +/- 10 heads\n")
            file.write("   21 central probabilities are practically equal.\n")
            file.write("   P(|k-N/2| <= 10) = " + format(probability_within_10, ".12E") + "\n\n")

            file.write("d) Cumulative probability within +/- 20 heads\n")
            file.write("   41 central probabilities are practically equal.\n")
            file.write("   P(|k-N/2| <= 20) = " + format(probability_within_20, ".12E") + "\n\n")

            file.write("e) Entropy difference for N/2 + 25 versus N/2\n")
            file.write("   Delta S approximately -2*k_B*25^2/N\n")
            file.write("   Delta S = " + format(delta_s_25, ".12E") + " J/K\n\n")

            file.write("f) Entropy difference for N/2 + 10 versus N/2\n")
            file.write("   Delta S approximately -2*k_B*10^2/N\n")
            file.write("   Delta S = " + format(delta_s_10, ".12E") + " J/K\n\n")

            file.write("g) Entropy difference between N/2 and 20 heads\n")
            file.write("   Delta S = S(N/2) - S(20)\n")
            file.write("   Delta S = " + format(delta_s_central_vs_20, ".12E") + " J/K\n\n")

            file.write("h) Expected waiting time for exactly 8 heads\n")
            file.write("   log10(P(k=8)) = " + str(log10_probability_8) + "\n")
            file.write("   log10(expected waiting time in seconds) = ")
            file.write(str(log10_waiting_time) + "\n")
            file.write("   Thus the waiting time is approximately 10 raised to this exponent seconds.\n\n")

            file.write("i) Likelihood ratio: central macrostate / macrostate N/2 + 10\n")
            file.write("   log(ratio) approximately 2*10^2/N = ")
            file.write(str(log_likelihood_ratio) + "\n")
            file.write("   Ratio approximately 1 + " + format(likelihood_ratio_excess, ".12E") + "\n\n")

            file.write("j) Second Law interpretation\n")
            file.write("   The Second Law is statistical, not an absolute prohibition of entropy-decreasing\n")
            file.write("   fluctuations. A lower-entropy macrostate is possible, but it has fewer\n")
            file.write("   compatible microstates and therefore a much smaller probability. The central\n")
            file.write("   macrostate is overwhelmingly favoured over strongly ordered states such as\n")
            file.write("   k=20. For N=10^23, a fluctuation from the central region to such a state is\n")
            file.write("   extraordinarily unlikely, but it is not mathematically forbidden. Thus the\n")
            file.write("   results do not contradict the Second Law: they explain its statistical meaning.\n\n")

            file.write("Large-N conclusions\n")
            file.write("   Standard deviation: sqrt(N)/2 = "
                       + format(N_decimal.sqrt() / Decimal(2), ".12E") + " heads.\n")
            file.write("   Relative fluctuation: 1/sqrt(N) = 3.16227766017E-12.\n")
            file.write("   For fixed k, P(k) approximately N^k/(k!*2^N), which tends to zero\n")
            file.write("   exponentially as N increases. The central single-macrostate probability\n")
            file.write("   also tends to zero, approximately as N^(-1/2).\n")
            file.write("   A fixed window of +/-10 or +/-20 heads is negligible compared with the\n")
            file.write("   fluctuation width, which grows as sqrt(N).\n")
            file.write("   For a fixed offset m from N/2, Delta S is approximately -2*k_B*m^2/N\n")
            file.write("   and tends to zero. In contrast, S(N/2)-S(20) grows approximately as\n")
            file.write("   N*k_B*ln(2). The likelihood ratio for a fixed offset tends to 1.\n")

    print("\nSECTION 2k FINISHED: LARGE N")
    print("N = 10^23")
    print("P(k=N/2):", probability_central)
    print("P(within +/- 10):", probability_within_10)
    print("P(within +/- 20):", probability_within_20)
    print("Delta S for +25 heads (J/K):", delta_s_25)
    print("Delta S for +10 heads (J/K):", delta_s_10)
    print("Delta S between centre and 20 heads (J/K):", delta_s_central_vs_20)
    print("log10(expected waiting time in seconds):", log10_waiting_time)
    print("Likelihood ratio: 1 +", likelihood_ratio_excess)
    print("All large-N results saved in:", output_file)


# ---------------------------------------------------------
# COMPILE THE LATEX REPORT
# ---------------------------------------------------------

def compile_latex_report():
    """Compile report/main.tex after the calculations and figures are ready.

    The function first tries latexmk. If it is not installed, it runs
    pdflatex twice so that references and figure numbers are updated.
    A missing LaTeX installation or a compilation error is reported clearly,
    but does not erase or interrupt the calculation results already produced.
    """

    report_file = REPORT_FOLDER / "main.tex"

    if not report_file.exists():
        print("LaTeX report not found:", report_file)
        print("Skipping report compilation.")
        return False

    latexmk = shutil.which("latexmk")
    pdflatex = shutil.which("pdflatex")

    if latexmk is not None:
        commands = [[
            latexmk,
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "main.tex",
        ]]
    elif pdflatex is not None:
        commands = [[
            pdflatex,
            "-interaction=nonstopmode",
            "-halt-on-error",
            "main.tex",
        ]] * 2
    else:
        print("LaTeX was not found (latexmk or pdflatex).")
        print("The calculations are complete, but the PDF was not compiled.")
        return False

    for command in commands:
        result = subprocess.run(
            command,
            cwd=REPORT_FOLDER,
            text=True,
            capture_output=True,
            check=False,
        )

        if result.returncode != 0:
            print("LaTeX compilation failed. Check report/main.log for details.")
            error_text = result.stdout + "\n" + result.stderr
            print(error_text[-3000:])
            return False

    pdf_file = REPORT_FOLDER / "main.pdf"
    if pdf_file.exists():
        print("LaTeX report compiled successfully:", pdf_file)
        return True

    print("LaTeX command finished, but report/main.pdf was not created.")
    return False


# ---------------------------------------------------------
# RUN THE PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    enumerate_seven_coins()
    make_distribution_plots()
    show_thermodynamic_limit()
    run_section_2()
    run_large_n_section_2()

    # Set the corresponding option to True at the top of this file
    # when you are ready to run the longer benchmark tasks.
    if RUN_ENUMERATION_BENCHMARK:
        run_enumeration_benchmark()

    if RUN_DISTRIBUTION_TEST:
        test_distribution_sizes()

    # Compile only after the calculations and plots have been generated.
    if COMPILE_LATEX_REPORT:
        compile_latex_report()
