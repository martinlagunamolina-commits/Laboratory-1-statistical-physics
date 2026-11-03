"""
Five-minute performance benchmark for microstate enumeration.
"""

import multiprocessing
import resource
import time

from collections.abc import Callable
from multiprocessing.connection import Connection

from src.microstates import (
    count_macrostate_multiplicities,
    count_macrostate_multiplicities_fast
)


def benchmark_worker(
    function: Callable[[int], dict[int, int]],
    N: int,
    connection: Connection
) -> None:
    """
    Execute an enumeration function and measure its time and peak RAM.
    """

    try:
        start = time.perf_counter()

        function(N)

        elapsed = time.perf_counter() - start

        # Peak resident memory in MB (Linux).
        peak_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

        connection.send({
            "completed": True,
            "time_seconds": elapsed,
            "peak_ram_mb": peak_ram
        })

    except Exception as error:

        connection.send({
            "completed": False,
            "error": str(error)
        })

    finally:
        connection.close()


def benchmark_once(
    function: Callable[[int], dict[int, int]],
    N: int,
    time_limit: float = 300.0
) -> dict:

    """
    Run one enumeration benchmark with a maximum wall-clock time.
    """

    context = multiprocessing.get_context("spawn")

    parent_connection, child_connection = context.Pipe(duplex=False)

    process = context.Process(
        target=benchmark_worker,
        args=(function, N, child_connection)
    )

    process.start()
    child_connection.close()

    # Wait for the process, but stop it after the time limit.
    process.join(time_limit)

    if process.is_alive():

        process.terminate()
        process.join()

        parent_connection.close()

        return {
            "completed": False,
            "timed_out": True
        }

    if parent_connection.poll():
        result = parent_connection.recv()
    else:
        result = {
            "completed": False,
            "error": "The benchmark process did not return a result."
        }

    parent_connection.close()

    return result


def find_max_N(
    function: Callable[[int], dict[int, int]],
    name: str,
    time_limit: float = 300.0,
    start_N: int = 20,
    step: int = 2
) -> int | None:

    """
    Find the largest tested N that can be fully enumerated
    within the specified time limit.
    """

    print(f"\n{name}")
    print("-" * 75)

    N = start_N
    largest_completed_N = None

    while True:

        print(f"\nTesting N = {N} ({1 << N:,} microstates)...")

        result = benchmark_once(function, N, time_limit)

        if result["completed"]:

            elapsed = result["time_seconds"]
            memory = result["peak_ram_mb"]

            print(f"Completed in {elapsed:.3f} seconds")
            print(f"Peak process RAM: {memory:.3f} MB")

            largest_completed_N = N
            N += step

        elif result.get("timed_out", False):

            print(f"Did not finish within {time_limit:.0f} seconds.")
            break

        else:

            print(f"Benchmark error: {result.get('error')}")
            return largest_completed_N

    # Test the intermediate N to find the largest integer N.
    if largest_completed_N is not None and step == 2:

        candidate_N = largest_completed_N + 1

        print(f"\nRefining the result by testing N = {candidate_N}...")

        result = benchmark_once(function, candidate_N, time_limit)

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


def run_five_minute_challenge() -> None:
    """
    Compare the original and optimized enumeration algorithms.
    """

    time_limit = 300.0

    original_max = find_max_N(
        count_macrostate_multiplicities,
        "ORIGINAL ENUMERATION",
        time_limit
    )

    optimized_max = find_max_N(
        count_macrostate_multiplicities_fast,
        "OPTIMIZED ENUMERATION",
        time_limit
    )

    print("\nFINAL COMPARISON")
    print("-" * 75)

    print(f"Original maximum N:  {original_max}")
    print(f"Optimized maximum N: {optimized_max}")


if __name__ == "__main__":
    run_five_minute_challenge()