import argparse
import sys
import csv
import json

from .iterated_radon import IteratedRadon
from .iterated_tverberg import IteratedTverberg
from .helpers import has_valid_dimension, has_valid_type, NumpyAwareJSONEncoder
from .benchmark import  benchmark


def parse_arguments(argv):
    """
    Initialize the CLI and parse the given argument.
    argv must not contain the filename in argv[0]

    :param argv:
    """

    # TODO: Tests

    parser = argparse.ArgumentParser(
        description="Calculate approximate centerpoints in higher-dimensions.")

    parser.add_argument("--benchmark", default=0, type=int,
                        metavar="NUM",
                        help="Run the specified centerpoint algorithm NUM "
                             "times and return a JSON tuple "
                             "(timings, results).")

    algo_group = parser.add_argument_group("Algorithms")
    algo_group_algos = algo_group.add_mutually_exclusive_group(required=True)
    algo_group_algos.add_argument("--radon", "--iterated-radon", "-1",
                                  action="store_true",
                                  help="Use the IteratedRadon algorithm "
                                       "introduced by Clarkson et al.")
    algo_group_algos.add_argument("--tverberg", "--iterated-tverberg", "-2",
                                  action="store_true",
                                  help="Use the IteratedTverberg algorithm "
                                       "introduced by Miller and Sheehy.")
    algo_group_algos.add_argument("--mulzer", "-3",
                                  action="store_true",
                                  help="Use the algorithm introduced by Mulzer"
                                       " and Werner.")

    radon_group = parser.add_argument_group("Iterated Radon Options")
    radon_group.add_argument("--radon-tree", action="store_true",
                             help="Use the subexponentially dependent on d "
                                  "Alogrithm 1.")
    #radon_group.add_argument("--radon-tree-height" ...)

    parser.add_argument("points", type=argparse.FileType('r'),
                        metavar="POINTS",
                        help='File containing the points (see also Input'
                             'Formats). To read from stdin use "-".')

    format_group = parser.add_argument_group("Input format")
    format_group = format_group.add_mutually_exclusive_group(required=False)
    format_group.add_argument("--csv", type=str, default="\t", metavar="SEP",
                              help="Read from a csv file separated by SEP"
                                   " (default: \\t) (default).")
    format_group.add_argument("--json", action="store_true",
                              help="Read from a json file.")

    args = parser.parse_args(argv)

    # Cleanup format
    if args.json:
        args.format = "json"
    else:
        args.format = "csv"

    args.separator = args.csv
    del args.json, args.csv

    return args


def read_points_csv(file, delimiter):
    reader = csv.reader(file, delimiter=delimiter)

    points = []
    for row in reader:
        # Transform strings to floats, assuming they are . separated.
        # TODO: throw custom error if reading failed
        point = list(map(float, row))
        points.append(point)

    return points


def read_points_json(file):
    # Load the json file and convert ints to float.
    # TODO: throw custom error if reading failed
    points = json.load(file, parse_int=float)

    return points


def main():
    # Initialize and parse the arguments.
    options = parse_arguments(sys.argv[1:])

    # Read the points from the file.
    try:
        if options.format == "csv":
            points = read_points_csv(options.points, options.separator)
        elif options.format == "json":
            points = read_points_json(options.points)
    finally:
        options.points.close()

    # Validate the dimension is correct.
    if not has_valid_dimension(points):
        raise TypeError("Invalid dimension for some point.")

    # Validate that every point consists of floats.
    if not has_valid_type(points, float):
        raise TypeError("Invalid format for some point.")

    algorithm = None
    if options.radon:
        algorithm = IteratedRadon(options.radon_tree)

    elif options.tverberg:
        algorithm = IteratedTverberg()

    elif options.mulzer:
        raise NotImplementedError()

    if options.benchmark > 0:
        result = benchmark(algorithm, points, options.benchmark)

        json.dump(result, sys.stdout,
                  cls=NumpyAwareJSONEncoder,
                  # indent=4, separators=(',', ': ')
                  )
        print()  # \n

    else:
        result = algorithm.centerpoint(points)

        # TODO: discuss if this is our intent?
        if options.format == "csv":
            writer = csv.writer(sys.stdout, delimiter=options.separator)
            writer.writerow(result)

        elif options.format == "json":
            json.dump(result, sys.stdout,
                      # indent=4, separators=(',', ': ')
                      )
            print()  # \n
