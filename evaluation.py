#!/usr/bin/env python
import argparse
import csv
import json
import random
from os import path

import numpy as np

from centerpoints.benchmark import benchmark

from centerpoints.helpers import uniform_sphere_points, \
    uniform_sphere_points_volume, normal_distributed_points, \
    NumpyAwareJSONEncoder
from centerpoints.iterated_radon import IteratedRadon
from centerpoints.iterated_tverberg import IteratedTverberg


# Initialize the algorithms
algorithms = (
    (IteratedTverberg(), "IteratedTverberg"),
    (IteratedRadon(), "IteratedRadon"),
    (IteratedRadon(True), "IteratedRadon (w/ Trees)")
)


# Wrappers to generators with less parameters
def _(gen):
    return lambda n, dim, r: gen(n, dim)


def __(gen):
    return lambda n, dim, r: gen(n)


# Benchmark configs
def benchmarks(repeat=None, size=None, radius=None):
    return {
        "circle": {
            "title": "Circle",
            "generator": uniform_sphere_points,
            "repeat": repeat,
            "size": size,
            "radius": radius,
            "dim": 2
        },

        "sphere": {
            "title": "Sphere",
            "generator": uniform_sphere_points,
            "repeat": repeat,
            "size": size,
            "radius": radius,
            "dim": 3
        },

        "sphere-solid": {
            "title": "Solid Sphere",
            "generator": uniform_sphere_points_volume,
            "repeat": repeat,
            "size": size,
            "radius": radius,
            "dim": 3
        },

        "sphere-10d": {
            "title": "Sphere (10D)",
            "generator": uniform_sphere_points,
            "repeat": repeat,
            "size": size,
            "radius": radius,
            "dim": 10
        },

        "normal-2d": {
            "title": "Normal distribution (2D)",
            "generator": _(normal_distributed_points),
            "repeat": repeat,
            "size": size,
            "radius": None,
            "dim": 2
        },

        "normal-3d": {
            "title": "Normal distribution (3D)",
            "generator": _(normal_distributed_points),
            "repeat": repeat,
            "size": size,
            "radius": None,
            "dim": 3
        },

        "normal-10d": {
            "title": "Normal distribution (10D)",
            "generator": _(normal_distributed_points),
            "repeat": repeat,
            "size": size,
            "radius": None,
            "dim": 10
        },

        # "cube": ..
    }


def run_benchmarks(benchmarks, output_dir, seed):

    # Truncate results and write header
    with open(path.join(output_dir, "results.csv"), "w") as f:
        writer = csv.writer(f)
        bench_short_result_titles = (
            "Name", "Title", "Algorithm",
            "Repeat", "Size", "Radius", "Dimension",
            "Min time", "Max time", "Mean time", "Median time",
            "Min distance", "Max distance",
            "Mean distance", "Median distance"
        )
        writer.writerow(bench_short_result_titles)

    # Run the benchmarks
    for name, config in benchmarks.items():
        # Export config
        title = config["title"]
        generator = config["generator"]
        repeat = config["repeat"]
        size = config["size"]
        radius = config["radius"]
        dim = config["dim"]

        print("Generating points for " + title)

        if seed:
            # Reset the seed to generate the same point sets
            random.seed(seed)
            np.random.seed(seed)

        points = generator(size, dim, radius)

        for algorithm in algorithms:
            print("Run " + title + " with " + algorithm[1])

            # TODO: Reset seed again????
            timings, results = benchmark(algorithm[0], points, repeat)

            # Calculate the distance to 0
            distances = np.linalg.norm(results, axis=1)

            # Calculate stats about the min, max and average
            _timings = np.asarray(timings)
            stats = (
                np.amin(_timings),
                np.max(_timings),
                np.mean(_timings),
                np.median(_timings)
            )

            dist_stat = (
                np.amin(distances),
                np.max(distances),
                np.mean(distances),
                np.median(distances)
            )

            _config = config.copy()
            del _config['generator']

            bench_result = {
                "algorithm": algorithm[1],
                "config": _config,
                "timings": timings,
                "results": results,
                "distances": distances,
                "dist_stat": dist_stat,
                "stats": stats,
                "seed": seed
            }

            # Store the results as csv and json
            algoname = type(algorithm[0]).__name__
            basename = path.join(output_dir, name + "-" + algoname)
            # with open(baseFileName + ".csv", mode="w") as f:
            # writer = csv.writer(f)
            #     writer.writerows(zip(timings, results, distances))

            with open(basename + ".json", mode="w") as f:
                json.dump(bench_result, f,
                          cls=NumpyAwareJSONEncoder,
                          indent=4, separators=(',', ': '))

            # Write a short summary to the combined results.
            bench_short_result = [name, title, algorithm[1],
                                  repeat, size, radius, dim]
            bench_short_result.extend(stats)
            bench_short_result.extend(dist_stat)

            with open(path.join(output_dir, "results.csv"), "a") as f:
                writer = csv.writer(f)
                writer.writerow(bench_short_result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Run multiple centerpoint benchmarks.")

    parser.add_argument("--repeat", type=int, default=10, required=False,
                        help="Repeat each benchmark REPEAT times.")
    parser.add_argument("--size", type=int, default=5000, required=False,
                        help="Generate SIZE points for each benchmark.")
    parser.add_argument("--radius", type=int, default=50, required=False,
                        help="Set the radius if applicable (f.ex. spheres).")
    parser.add_argument("--seed", type=int, default=None, required=False,
                        help="Generate random points based on this seed. "
                             "Can be used to reproduce results.")
    parser.add_argument("--output-dir", type=str, default=None, required=False,
                        help="Write results to output-dir. "
                             "Default ./evaluation .")
    parser.add_argument("benchmarks", nargs="*",
                        help="Benchmarks to run. "
                             "If omitted every benchmark is run. "
                             "Possible values: " +
                             ", ".join(benchmarks().keys())
    )

    args = parser.parse_args()

    if not args.output_dir:
        _dirname = path.dirname(path.realpath(__file__))
        args.output_dir = path.join(_dirname, "evaluation")

    # Only run the specified benchmarks
    _benchmarks = benchmarks(args.repeat, args.size, args.radius)
    if args.benchmarks:
        _benchmarks = {name: config
                       for (name, config)
                       in _benchmarks.items()
                       if name in args.benchmarks}

    # Run run run!
    run_benchmarks(_benchmarks, args.output_dir, args.seed)
