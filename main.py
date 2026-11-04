"""Generate all lab data, vector figures and LaTeX result fragments.

Run directly with the team's default suffixes 71, 95, 11, 79:
    python main.py
Optional overrides:
    python main.py --nia 71 95 11 79 --rounding nearest
"""
import argparse
import csv
import json
from fractions import Fraction
from math import ceil, exp, floor, log, log10
from pathlib import Path
import platform
import sys
import numpy as np
import scipy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.microstates import enumerate_microstates, count_heads, state_string
from src.combinatorics import (exact_multiplicities, log_distribution, log_probability,
                               cumulative_probability, log_multiplicity_gammaln)
from src.thermodynamics import K_B, entropy_difference, integer_system_size, log10_waiting_time

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = ROOT / "report"
FIGURES = REPORT / "figures"


def write_csv(path: Path, header: list[str], rows) -> None:
    """Write a UTF-8 CSV with a header; exact integers remain decimal strings."""
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def sci(value: float) -> str:
    """Format a finite value for LaTeX at six significant figures."""
    if value == 0:
        return "0"
    mantissa, exponent = f"{value:.5e}".split("e")
    return rf"{mantissa}\times10^{{{int(exponent)}}}"


def generate_microstates() -> None:
    """Export all 128 seven-coin configurations, grouped by macrostate."""
    groups = {k: [] for k in range(8)}
    for state in enumerate_microstates(7):
        groups[count_heads(state)].append(state_string(state, 7))
    write_csv(RESULTS / "microstates_N7.csv", ["heads", "tails", "microstate"],
              ((k, 7-k, state) for k, states in groups.items() for state in states))
    text = []
    for k, states in groups.items():
        text.append(rf"\noindent\textbf{{{k} heads, {7-k} tails; $\Omega={len(states)}$:}}\par\smallskip")
        text.append(r"\begin{tabular}{@{}llllllll@{}}")
        for index in range(0,len(states),8):
            text.append(" & ".join(r"\texttt{"+s+"}" for s in states[index:index+8]) + r" \\")
        text.append(r"\end{tabular}\par\medskip")
    (REPORT / "microstates_N7.tex").write_text("\n".join(text) + "\n")


def generate_distributions() -> None:
    """Export exact part 1.c coefficients and plot raw and normalized curves."""
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.6), constrained_layout=True)
    for N in (20, 50, 80, 100):
        counts = exact_multiplicities(N)
        k, logs = log_distribution(N)
        probabilities = np.exp(logs - N * log(2))
        write_csv(RESULTS / f"distribution_N{N}.csv", ["heads", "multiplicity_exact", "probability", "ln_multiplicity"],
                  ((i, counts[i], f"{probabilities[i]:.16e}", f"{logs[i]:.16e}") for i in range(N+1)))
        axes[0].semilogy(k, counts, label=f"N={N}")
        axes[1].plot(k, probabilities, label=f"N={N}")
    axes[0].set(xlabel="Heads k (dimensionless)", ylabel="Multiplicity Omega (dimensionless)")
    axes[1].set(xlabel="Heads k (dimensionless)", ylabel="Probability P(K=k) (dimensionless)")
    for ax in axes:
        ax.legend(fontsize=8)
        ax.grid(alpha=0.2)
    fig.savefig(FIGURES / "macrostate_distributions.pdf")
    plt.close(fig)


def generate_group_results(digits: list[int] | None, rounding: str) -> None:
    """Write every part 2 numerical result, or explicit symbolic pending results."""
    symbolic = [
        ("2.a", r"P(K=30)", r"\binom{N}{30}2^{-N}"),
        ("2.b", r"P(K=k_0)", r"\binom{N}{k_0}2^{-N}"),
        ("2.c", r"P(|K-N/2|\leq10)", r"\sum_{k=\lceil N/2-10\rceil}^{\lfloor N/2+10\rfloor}P_k"),
        ("2.d", r"P(|(N-K)-N/2|\leq20)", r"\sum_{k=\lceil N/2-20\rceil}^{\lfloor N/2+20\rfloor}P_k"),
        ("2.e", r"\Delta S/k_B", r"\ln[\Omega(N,k_0+25)/\Omega(N,k_0)]"),
        ("2.f", r"\Delta S/k_B", r"\ln[\Omega(N,k_0+10)/\Omega(N,k_0)]"),
        ("2.g", r"\Delta S/k_B", r"\ln[\Omega(N,k_0)/\Omega(N,20)]"),
        ("2.h", r"\mathbb{E}T\ (\mathrm{s})", r"2^N/\binom{N}{8}"),
        ("2.i", r"R_-,R_+", r"\Omega(N,k_0)/\Omega(N,q_\pm)"),
    ]
    tex = [r"\begin{tabular}{lll}\toprule Part & Quantity & Result \\\midrule"]
    if not digits:
        status = (r"\textbf{Group-specific values pending:} no NIA suffixes were provided. "
                  r"The complete group suffix list is required. No numerical group parameter has been invented.")
        for part, quantity, expression in symbolic:
            tex.append(rf"{part} & ${quantity}$ & ${expression}$ \\")
        data = {"status": "pending_NIA_suffixes", "known_suffix": 71}
    else:
        M, N = integer_system_size(digits, rounding)
        center = N // 2
        # M +/-10 is literal manual wording; nearest-integer states, half-up.
        q_values = [floor(M - 10 + Fraction(1,2)), floor(M + 10 + Fraction(1,2))]
        data = dict(status="calculated", suffixes=digits, M_exact=str(M), M=float(M), N=N,
                    rounding=rounding, center=center,
                    P30=exp(log_probability(N, 30)), Pmode=exp(log_probability(N, center)),
                    Pwithin10=cumulative_probability(N, ceil(N/2-10), floor(N/2+10)),
                    Pwithin20tails=cumulative_probability(N, ceil(N/2-20), floor(N/2+20)),
                    deltaS_e_J_per_K=entropy_difference(N, center+25, center),
                    deltaS_f_J_per_K=entropy_difference(N, center+10, center),
                    deltaS_g_J_per_K=entropy_difference(N, center, 20),
                    log10_mean_wait_seconds=log10_waiting_time(N, 8),
                    log10_mean_wait_years=log10_waiting_time(N, 8)-log10(365.25*86400),
                    likelihood_states=q_values,
                    likelihood_log_ratios=[log_probability(N, center)-log_probability(N, q)
                                           if 0 <= q <= N else None for q in q_values],
                    centered_alternative_log_ratios=[log_probability(N, center)-log_probability(N, center+d)
                                                    for d in (-10, 10)])
        status = (rf"NIA suffixes: {', '.join(map(str,digits))}. "
                  rf"$M={M}={float(M):.8f}$; $N={N}$ ({rounding} rounding); $k_0={center}$. "
                  rf"For 2.i, $(q_-,q_+)=({q_values[0]},{q_values[1]})$. "
                  r"Rounding is provisional because the manual does not specify it.")
        vals = [sci(data["P30"]), sci(data["Pmode"]), sci(data["Pwithin10"]), sci(data["Pwithin20tails"]),
                sci(data["deltaS_e_J_per_K"]/K_B), sci(data["deltaS_f_J_per_K"]/K_B),
                sci(data["deltaS_g_J_per_K"]/K_B), sci(10**data["log10_mean_wait_seconds"]),
                r",\ ".join("\\text{undefined}" if x is None else sci(exp(x)) for x in data["likelihood_log_ratios"])]
        for (part, quantity, _), value in zip(symbolic, vals):
            tex.append(rf"{part} & ${quantity}$ & ${value}$ \\")
        tex += [r"\midrule"]
        for label in ("e", "f", "g"):
            tex.append(rf"2.{label} & $\Delta S\ (\mathrm{{J\,K^{{-1}}}})$ & ${sci(data['deltaS_'+label+'_J_per_K'])}$ \\")
    tex.append(r"\bottomrule\end{tabular}")
    (REPORT / "group_status.tex").write_text(status + "\n")
    (REPORT / "group_results.tex").write_text("\n".join(tex) + "\n")
    (RESULTS / "group_results.json").write_text(json.dumps(data, indent=2) + "\n")


def generate_benchmark_tables() -> None:
    """Insert actual recorded measurements without inventing missing runs."""
    for kind in ("enumeration", "distribution"):
        path = RESULTS / f"{kind}_benchmark.json"
        if not path.exists():
            text = r"Benchmark not yet run; execute the documented command on the submission laptop."
        else:
            data = json.loads(path.read_text())
            lines = [r"\begin{tabular}{rrrr}\toprule $N$ & Time (s) & Peak RSS (MiB) & Status \\\midrule"]
            for row in data["rows"]:
                seconds = (f"{row['seconds']:.3f}" if "seconds" in row else
                           rf">{row['timeout_seconds']:g}" if "timeout_seconds" in row else "---")
                memory = f"{row['peak_rss_mib']:.2f}" if "peak_rss_mib" in row else "---"
                status = row["status"].replace("_", r"\_")
                lines.append(rf"{row['N']} & ${seconds}$ & {memory} & {status} \\")
            lines.append(r"\bottomrule\end{tabular}")
            complete = [r["N"] for r in data["rows"] if r["status"] == "complete"]
            lines.append(rf"\par\smallskip Largest completed tested candidate: $N={max(complete) if complete else 0}$. ")
            lines.append(rf"Per-run wall-clock budget: {data['per_run_timeout_seconds']:g} s. ")
            if kind == "distribution":
                lines.append(rf"Peak-RSS budget: {data['rss_budget_mib']:g} MiB. Candidate grid is not exhaustive.")
            lines.append(r"\par\smallskip Platform: \texttt{" + data["platform"].replace("_", r"\_") + "}. ")
            lines.append(r"These measurements are from the recorded platform; consult the accompanying benchmark JSON for provenance.")
            calibration = RESULTS / "timing_calibration.json"
            if kind == "enumeration" and calibration.exists():
                c = json.loads(calibration.read_text())
                lines.append(rf"\par At $N=24$, five independent calibration runs gave mean time "
                             rf"${c['mean_seconds']:.3f}\pm{c['sample_sd_seconds']:.3f}$ s "
                             r"(sample standard deviation, not standard error). "
                             rf"Timer resolution: ${sci(c['timer_resolution_seconds'])}$ s. "
                             r"This variability estimate applies to the calibration workload.")
            text = "\n".join(lines)
        (REPORT / f"{kind}_benchmark.tex").write_text(text + "\n")


def main() -> None:
    """Create deterministic scientific outputs from supplied parameters."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--nia",
        type=int,
        nargs="+",
        default=[71, 95, 11, 79],
        help="Last-two-digit NIA suffixes of all team members",
    )
    parser.add_argument("--rounding", choices=["nearest", "floor", "ceil"], default="nearest")
    args = parser.parse_args()
    for directory in (RESULTS, REPORT, FIGURES):
        directory.mkdir(parents=True, exist_ok=True)
    generate_microstates()
    generate_distributions()
    generate_group_results(args.nia, args.rounding)
    generate_benchmark_tables()
    versions = {"python": sys.version, "platform": platform.platform(), "numpy": np.__version__,
                "scipy": scipy.__version__, "matplotlib": matplotlib.__version__}
    (RESULTS / "environment_used.json").write_text(json.dumps(versions, indent=2) + "\n")
    print("Generated all N=7 microstates, four exact distributions, vector figures and report fragments.")
    print("Group results: " + ("calculated from supplied suffixes." if args.nia else "pending missing NIA suffixes."))
    data = json.loads((RESULTS / "group_results.json").read_text())
    if data["status"] == "calculated":
        print(f"NIA suffixes: {data['suffixes']}; M={data['M']:.10f}; N={data['N']}; mode={data['center']}")
        for key in ("P30", "Pmode", "Pwithin10", "Pwithin20tails",
                    "deltaS_e_J_per_K", "deltaS_f_J_per_K", "deltaS_g_J_per_K",
                    "log10_mean_wait_seconds", "log10_mean_wait_years"):
            print(f"{key}: {data[key]:.10g}")
        print("Likelihood ratios (M-10, M+10):", [exp(x) if x is not None else None for x in data["likelihood_log_ratios"]])
    print(f"Data: {RESULTS}")
    print(f"Figures and LaTeX: {REPORT}; compile report/main.tex to update the PDF.")



if __name__ == "__main__":
    main()