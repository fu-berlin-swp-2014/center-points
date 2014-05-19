import argparse
import sys
import csv
import json

from centerpoints.helpers import has_valid_dimension, has_valid_type


def parse_arguments(argv):
    """
    Initialize the CLI and parse the given argument.
    argv must not contain the filename in argv[0]

    :param argv:
    """

    # TODO: Tests

    parser = argparse.ArgumentParser(
        description="Calculate approximate centerpoints in higher-dimensions.")

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
        point = map(float, row)
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

    result = None
    if options.radon:
        pass
    elif options.tverberg:
        pass
    elif options.mulzer:
        pass

    print(result)