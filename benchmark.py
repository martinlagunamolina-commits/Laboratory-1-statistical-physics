"""Isolated wall-clock and peak-RSS measurements, not fabricated estimates.

Run enumeration in a subprocess for each N and kill the first timed-out run.
Each complete run consumes every yielded integer; it does not format or print
all configurations. This distinction matters when interpreting the 5-min limit.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import statistics
import sys
import time
from src.microstates import enumerate_microstates


def peak_rss_mib() -> float:
    """Return process peak resident memory on Windows, Linux or macOS."""
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_ = [("cb",wintypes.DWORD),("PageFaultCount",wintypes.DWORD)] + [
                (name,ctypes.c_size_t) for name in ("PeakWorkingSetSize","WorkingSetSize",
                "QuotaPeakPagedPoolUsage","QuotaPagedPoolUsage","QuotaPeakNonPagedPoolUsage",
                "QuotaNonPagedPoolUsage","PagefileUsage","PeakPagefileUsage")]
        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        kernel = ctypes.WinDLL("kernel32",use_last_error=True)
        psapi = ctypes.WinDLL("psapi",use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
        if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ctypes.byref(counters),counters.cb):
            raise ctypes.WinError(ctypes.get_last_error())
        return counters.PeakWorkingSetSize/(1024**2)
    import resource
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rss/(1024**2 if sys.platform == "darwin" else 1024)


def worker(kind: str, N: int) -> dict:
    """Measure one workload; ru_maxrss is process-wide peak resident RAM."""
    start = time.perf_counter()
    if kind == "enumeration":
        count = 0
        for state in enumerate_microstates(N):
            count += 1
        assert count == 1 << N
        retained_bytes = 0
    else:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from src.combinatorics import log_distribution
        k, logs = log_distribution(N)
        retained_bytes = k.nbytes + logs.nbytes
        fig, ax = plt.subplots()
        ax.plot(k, logs, rasterized=False)
        ax.set(xlabel="Heads k (dimensionless)", ylabel="ln multiplicity (dimensionless)")
        fig.savefig(Path("results") / "distribution_stress.pdf")
        plt.close(fig)
    elapsed = time.perf_counter() - start
    rss_mib = peak_rss_mib()
    return dict(N=N, seconds=elapsed, peak_rss_mib=rss_mib, retained_bytes=retained_bytes)


def run_suite(kind: str, sizes: list[int], seconds: float, ram_mib: float | None = None) -> dict:
    """Record completed/failed candidates and stop at the first limit breach."""
    rows = []
    for N in sizes:
        command = [sys.executable, __file__, "--worker", kind, "--N", str(N)]
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=seconds)
            if proc.returncode:
                rows.append(dict(N=N, status="failed", error=proc.stderr[-500:]))
                break
            row = json.loads(proc.stdout)
            row["status"] = "complete" if ram_mib is None or row["peak_rss_mib"] <= ram_mib else "over_ram_budget"
            rows.append(row)
            if row["status"] != "complete":
                break
        except subprocess.TimeoutExpired:
            rows.append(dict(N=N, status="timeout", timeout_seconds=seconds))
            break
    return dict(kind=kind, python=sys.version, platform=platform.platform(),
                processor=platform.processor(), cpu_count=os.cpu_count(),
                per_run_timeout_seconds=seconds, rss_budget_mib=ram_mib, rows=rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=["enumeration", "distribution"])
    parser.add_argument("--N", type=int, default=20)
    parser.add_argument("--kind", choices=["enumeration", "distribution"], default="enumeration")
    parser.add_argument("--start", type=int, default=20)
    parser.add_argument("--stop", type=int, default=36)
    parser.add_argument("--seconds", type=float, default=300)
    parser.add_argument("--calibration", action="store_true", help="Five N=24 repetitions for timing variability")
    args = parser.parse_args()
    Path("results").mkdir(exist_ok=True)
    if args.worker:
        print(json.dumps(worker(args.worker, args.N)))
    elif args.calibration:
        result = run_suite("enumeration", [24]*5, 10)
        timings = [r["seconds"] for r in result["rows"] if r["status"] == "complete"]
        if len(timings) != 5:
            raise RuntimeError("Calibration did not complete five runs.")
        result["mean_seconds"] = statistics.mean(timings)
        result["sample_sd_seconds"] = statistics.stdev(timings)
        result["timer_resolution_seconds"] = time.get_clock_info("perf_counter").resolution
        path = Path("results/timing_calibration.json")
        path.write_text(json.dumps(result, indent=2) + "\n")
        print(path.read_text())
    else:
        sizes = list(range(args.start, args.stop + 1)) if args.kind == "enumeration" else [1000, 10000, 100000, 1000000, 2000000, 4000000]
        result = run_suite(args.kind, sizes, args.seconds, 256 if args.kind == "distribution" else None)
        path = Path("results") / (args.kind + "_benchmark.json")
        path.write_text(json.dumps(result, indent=2) + "\n")
        print(path.read_text())