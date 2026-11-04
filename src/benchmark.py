"""Five-minute performance benchmark for full microstate enumeration (Linux)."""

from __future__ import annotations

import csv
import multiprocessing
import resource
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from multiprocessing.connection import Connection

from src.microstates import (
    count_macrostate_multiplicities,
    count_macrostate_multiplicities_fast,
)


EnumerationFunction = Callable[[int], dict[int, int]]


def benchmark_worker(
    function: EnumerationFunction,
    N: int,
    connection: Connection,
) -> None:
    """Run one enumeration and report elapsed time, peak RAM, and validation."""
    try:
        start = time.perf_counter()
        multiplicities = function(N)
        elapsed = time.perf_counter() - start

        # Validate the result after the timed section so validation does not
        # contribute to the reported enumeration time.
        expected_keys = set(range(N + 1))
        if set(multiplicities) != expected_keys:
            raise RuntimeError("The result does not contain every macrostate k=0,...,N.")

        total_counted = sum(multiplicities.values())
        expected_total = 1 << N
        if total_counted != expected_total:
            raise RuntimeError(
                f"Incorrect total: counted {total_counted}, expected {expected_total}."
            )

        # On Linux, ru_maxrss is reported in KiB. Divide by 1024 for MiB.
        peak_ram_mib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

        connection.send(
            {
                "completed": True,
                "time_seconds": elapsed,
                "peak_ram_mib": peak_ram_mib,
                "total_microstates": total_counted,
                "validation_passed": True,
            }
        )

    except Exception as error:
        connection.send({"completed": False, "error": str(error)})

    finally:
        connection.close()


def benchmark_once(
    function: EnumerationFunction,
    N: int,
    time_limit: float = 300.0,
) -> dict[str, Any]:
    """Run one benchmark in a separate process with a wall-clock time limit."""
    context = multiprocessing.get_context("spawn")
    parent_connection, child_connection = context.Pipe(duplex=False)

    process = context.Process(
        target=benchmark_worker,
        args=(function, N, child_connection),
    )
    process.start()
    child_connection.close()

    process.join(time_limit)

    if process.is_alive():
        process.terminate()
        process.join()
        parent_connection.close()
        return {"completed": False, "timed_out": True}

    if parent_connection.poll():
        result = parent_connection.recv()
    else:
        result = {
            "completed": False,
            "error": f"Worker exited without returning a result (exit code {process.exitcode}).",
        }

    parent_connection.close()
    return result


def find_max_N(
    function: EnumerationFunction,
    name: str,
    time_limit: float = 300.0,
    start_N: int = 20,
    step: int = 2,
    measurements: list[dict[str, Any]] | None = None,
) -> int | None:
    """Find the largest integer N completed within the time limit.

    N is first increased in increments of ``step``. With the default step=2,
    the one integer between the final completed and timed-out tests is checked
    separately, so the largest consecutive integer N is identified.
    """
    print(f"\n{name}\n" + "-" * 75)
    N = start_N
    largest_completed_N: int | None = None

    def record(test_N: int, result: dict[str, Any]) -> None:
        if measurements is None:
            return
        measurements.append(
            {
                "algorithm": name,
                "N": test_N,
                "microstates": 1 << test_N,
                "completed": result.get("completed", False),
                "timed_out": result.get("timed_out", False),
                "time_seconds": result.get("time_seconds", ""),
                "peak_ram_mib": result.get("peak_ram_mib", ""),
                "validation_passed": result.get("validation_passed", False),
                "error": result.get("error", ""),
            }
        )

    while True:
        print(f"\nTesting N = {N} ({1 << N:,} microstates)...")
        result = benchmark_once(function, N, time_limit)
        record(N, result)

        if result["completed"]:
            print(f"Completed in {result['time_seconds']:.3f} seconds")
            print(f"Peak process RAM: {result['peak_ram_mib']:.3f} MiB")
            print(f"Validation: {result['total_microstates']:,} microstates counted")
            largest_completed_N = N
            N += step

        elif result.get("timed_out", False):
            print(f"Did not finish within {time_limit:.0f} seconds.")
            break

        else:
            print(f"Benchmark error: {result.get('error')}")
            return largest_completed_N

    # With step=2, check the single integer between the last success and failure.
    if largest_completed_N is not None and step == 2:
        candidate_N = largest_completed_N + 1
        print(f"\nRefining the result by testing N = {candidate_N}...")
        result = benchmark_once(function, candidate_N, time_limit)
        record(candidate_N, result)

        if result["completed"]:
            largest_completed_N = candidate_N
            print(
                f"N = {candidate_N} completed in "
                f"{result['time_seconds']:.3f} seconds."
            )
        elif result.get("timed_out", False):
            print(f"N = {candidate_N} exceeded the time limit.")
        else:
            print(f"Benchmark error: {result.get('error')}")

    print(f"\nLargest completed N for {name}: {largest_completed_N}")
    return largest_completed_N


def run_five_minute_challenge(
    output_csv: str | Path | None = None,
) -> dict[str, int | None]:
    """Compare both enumeration algorithms and optionally save all trial data."""
    time_limit = 300.0
    measurements: list[dict[str, Any]] = []

    original_max = find_max_N(
        count_macrostate_multiplicities,
        "ORIGINAL ENUMERATION",
        time_limit=time_limit,
        measurements=measurements,
    )
    optimized_max = find_max_N(
        count_macrostate_multiplicities_fast,
        "OPTIMIZED ENUMERATION (bit_count)",
        time_limit=time_limit,
        measurements=measurements,
    )

    print("\nFINAL COMPARISON\n" + "-" * 75)
    print(f"Original maximum N:  {original_max}")
    print(f"Optimized maximum N: {optimized_max}")

    if output_csv is not None:
        output_path = Path(output_csv)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "algorithm",
            "N",
            "microstates",
            "completed",
            "timed_out",
            "time_seconds",
            "peak_ram_mib",
            "validation_passed",
            "error",
        ]
        with output_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(measurements)
        print(f"Benchmark measurements saved to: {output_path}")

    return {
        "original_max_N": original_max,
        "optimized_max_N": optimized_max,
    }


if __name__ == "__main__":
    run_five_minute_challenge()
