#!/usr/bin/env python
import argparse
import csv
import json
import random
from os import path

import numpy as np
import scipy.stats


from centerpoints.benchmark import benchmark
from centerpoints.data_set import sphere_surface, sphere_volume, cube, \
    cube_surface

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


dim_benchmark_gens = {
    "sphere": uniform_sphere_points,
    "normal": _(normal_distributed_points),
    "sphere-solid": uniform_sphere_points_volume,
}


def dim_benchmarks(gens, repeat=None, size=None, radius=None, dim=None):
    benchmarks = {}

    for name, gen in gens.items():
        benchmark_name = "{}-{}n-{}d".format(name, size, dim)
        benchmark = {
            "title": benchmark_name,
            "generator": gen,
            "repeat": repeat,
            "size": size,
            "radius": radius,
            "dim": dim
        }

        benchmarks[benchmark_name] = benchmark

    return benchmarks


# Benchmark configs
def benchmarks(repeat=None, size=None, radius=None):
    return {
        "sphere": {
            "title": "Sphere Surface",
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

        "sphere-5d": {
            "title": "Sphere Surface (5D)",
            "generator": uniform_sphere_points,
            "repeat": repeat,
            "size": size,
            "radius": radius,
            "dim": 5
        },

        "sphere-5d-solid": {
            "title": "Solid Sphere (5D)",
            "generator": uniform_sphere_points_volume,
            "repeat": repeat,
            "size": size,
            "radius": radius,
            "dim": 5
        },

        "sphere-10d": {
            "title": "Sphere (10D)",
            "generator": uniform_sphere_points,
            "repeat": repeat,
            "size": 15000,
            "radius": radius,
            "dim": 10
        },

        "sphere-10d-solid": {
            "title": "Solid Sphere (10D)",
            "generator": uniform_sphere_points_volume,
            "repeat": repeat,
            "size": 15000,
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

        "normal-5d": {
            "title": "Normal distribution (3D)",
            "generator": _(normal_distributed_points),
            "repeat": repeat,
            "size": size,
            "radius": None,
            "dim": 5
        },

        "normal-10d": {
            "title": "Normal distribution (10D)",
            "generator": _(normal_distributed_points),
            "repeat": repeat,
            "size": 15000,
            "radius": radius,
            "dim": 10
        },

        # Other testdata
        "circle-surface": {
            "title": "Circle Surface b",
            "generator": _(sphere_surface),
            "repeat": repeat,
            "size": size,
            "radius": 1,
            "dim": 2
        },

        "circle-volume": {
            "title": "Circle Volume b",
            "generator": _(sphere_volume),
            "repeat": repeat,
            "size": size,
            "radius": 1,
            "dim": 2
        },

        "sphere-surface": {
            "title": "Sphere Surface b",
            "generator": _(sphere_surface),
            "repeat": repeat,
            "size": size,
            "radius": 1,
            "dim": 3
        },

        "sphere-volume": {
            "title": "Solid Volume b",
            "generator": _(sphere_volume),
            "repeat": repeat,
            "size": size,
            "radius": 1,
            "dim": 3
        },

        "sphere-surface-5d": {
            "title": "Sphere Surface 5D b",
            "generator": _(sphere_surface),
            "repeat": repeat,
            "size": size,
            "radius": 1,
            "dim": 5
        },

        "sphere-volume-5d": {
            "title": "Solid Volume 5D b",
            "generator": _(sphere_volume),
            "repeat": repeat,
            "size": size,
            "radius": 1,
            "dim": 5
        },

        # "sphere-surface-10d": {
        #     "title": "Sphere Surface 10D b",
        #     "generator": _(sphere_surface),
        #     "repeat": repeat,
        #     "size": 15000,
        #     "radius": 1,
        #     "dim": 10
        # },
        #
        # "sphere-volume-10d": {
        #     "title": "Solid Volume 10D b",
        #     "generator": _(sphere_volume),
        #     "repeat": repeat,
        #     "size": 15000,
        #     "radius": 1,
        #     "dim": 10
        # },

        "square-surface": {
            "title": "Square Surface b",
            "generator": _(cube_surface),
            "repeat": repeat,
            "size": size,
            "radius": 1,
            "dim": 2
        },

        "square-volume": {
            "title": "Square Volume b",
            "generator": _(cube),
            "repeat": repeat,
            "size": size,
            "radius": 1,
            "dim": 2
        },

        "cube-surface": {
            "title": "Cube Surface b",
            "generator": _(cube_surface),
            "repeat": repeat,
            "size": size,
            "radius": 1,
            "dim": 3
        },

        "cube-volume": {
            "title": "Cube Volume b",
            "generator": _(cube),
            "repeat": repeat,
            "size": size,
            "radius": 1,
            "dim": 3
        },

        "cube-surface-5d": {
            "title": "Cube Surface 5D b",
            "generator": _(cube_surface),
            "repeat": repeat,
            "size": size,
            "radius": 1,
            "dim": 5
        },

        "cube-volume-5d": {
            "title": "Cube Volume 5D b",
            "generator": _(cube),
            "repeat": repeat,
            "size": size,
            "radius": 1,
            "dim": 5
        },

    }


def run_benchmarks(benchmarks, output_dir, seed):

    # Truncate results and write header
    csv_file = open(path.join(output_dir, "results.csv"), "w")
    csv_writer = csv.writer(csv_file)
    bench_short_result_titles = (
        "Name", "Title", "Algorithm",
        "Repeat", "Size", "Radius", "Dimension",
        "min time", "max time", "mean time", "median time",
        "std time", "sem time",
        "min distance", "max distance",
        "mean distance", "median distance",
        "std distance", "sem distance"
    )
    csv_writer.writerow(bench_short_result_titles)

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

        try:
            points = generator(size, dim, radius)
        except Exception as e:
            print("Error on generating data:", e)
            import traceback
            traceback.print_exc()
            continue

        for i, algorithm in enumerate(algorithms):
            print("Run " + title + " with " + algorithm[1])

            # TODO: Reset seed again????
            try:
                timings, results = benchmark(algorithm[0], points, repeat)
            except Exception as e:
                print("Error on calculating centerpoint:", e)
                import traceback
                traceback.print_exc()
                continue

            # Calculate the distance to 0
            distances = np.linalg.norm(results, axis=1)

            # Calculate stats about the min, max and average
            _timings = np.asarray(timings)
            timings_stats = {
                "min": np.amin(_timings),
                "max": np.amax(_timings),
                "mean": np.mean(_timings),
                "median": np.median(_timings),
                "std": np.std(_timings),
                "sem": scipy.stats.sem(_timings)
            }

            distances_stats = {
                "min": np.amin(distances),
                "max": np.amax(distances),
                "mean": np.mean(distances),
                "median": np.median(distances),
                "std": np.std(distances),
                "sem": scipy.stats.sem(distances)
            }

            if np.isnan(timings_stats["sem"]):
                timings_stats["sem"] = 0

            if np.isnan(distances_stats["sem"]):
                distances_stats["sem"] = 0


            _config = config.copy()
            del _config['generator']

            bench_result = {
                "algorithm": algorithm[1],
                "config": _config,
                "timings": timings,
                "results": results,
                "distances": distances,
                "stats": {
                    'timings': timings_stats,
                    'distances': distances_stats
                },
                "seed": seed
            }

            # Store the results as csv and json
            algoname = type(algorithm[0]).__name__ + "-" + str(i)
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
            r = timings_stats
            bench_short_result.extend([r["min"], r["max"], r["mean"], r["median"], r["std"], r["sem"]])
            r = distances_stats
            bench_short_result.extend([r["min"], r["max"], r["mean"], r["median"], r["std"], r["sem"]])

            csv_writer.writerow(bench_short_result)
            csv_file.flush()

    csv_file.close()

def IntListType(argstr):
    if type(argstr) is None:
        return None

    return list(map(int, argstr.split(",")))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Run multiple centerpoint benchmarks.")

    parser.add_argument("--repeat", type=int, default=10, required=False,
                        help="Repeat each benchmark REPEAT times.")
    parser.add_argument("--sizes", type=IntListType, default=[5000],
                        required=False, help="Generate SIZES points for each "
                                             "benchmark without a fixed size.")
    parser.add_argument("--radius", type=int, default=50, required=False,
                        help="Set the radius if applicable (f.ex. spheres).")
    parser.add_argument("--dimensions", type=IntListType, default=None, required=False,
                        help="Use special dimensions case... to be documented.")
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
    _benchmarks = {}

    for size in args.sizes:
        if args.dimensions:
            _gens = {name: gen
                     for (name, gen)
                     in dim_benchmark_gens.items()
                     if not args.benchmarks or name in args.benchmarks}

            for dim in args.dimensions:
                _dim_benchmarks = dim_benchmarks(_gens, args.repeat, size,
                                                 args.radius, dim)
                _benchmarks.update(_dim_benchmarks)

        else:
            avialible_benchmarks = benchmarks(args.repeat, size, args.radius)
            if args.benchmarks:
                _benchmarks.update(
                    {"{}-{}n".format(name, size): config
                     for (name, config)
                     in avialible_benchmarks.items()
                     if name in args.benchmarks})

    # Run run run!
    run_benchmarks(_benchmarks, args.output_dir, args.seed)
