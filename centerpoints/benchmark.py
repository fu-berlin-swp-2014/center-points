import time
import gc


def benchmark(centerpoint_algo, points, repeat):
    timer = time.perf_counter

    # Turn off gc
    gcold = gc.isenabled()
    gc.disable()
    try:
        timed_results = _timeit(centerpoint_algo, points, timer, repeat)
    finally:
        if gcold:
            gc.enable()

    return timed_results


def _timeit(centerpoint_algo, points, _timer, repeat):
    results = [None] * repeat
    timings = [None] * repeat
    for _i in range(repeat):
        _t0 = _timer()
        r = centerpoint_algo.centerpoint(points)
        _t1 = _timer()

        results[_i] = r
        timings[_i] = _t1 - _t0

    return timings, results