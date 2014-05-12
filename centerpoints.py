import argparse
import sys
import csv


def parse_arguments(argv):
    """
    Initialize the CLI and parse the given argument.
    argv must not contain the filename in argv[0]

    :param argv:
    """

    # TODO: Tests

    parser = argparse.ArgumentParser(description="Calculate centerpoints in higher-dimensions.")

    algo_group = parser.add_argument_group("Algorithms")
    algo_group_algos = algo_group.add_mutually_exclusive_group(required=True)
    algo_group_algos.add_argument("--radon", "--iterated-radon", "-1",  action="store_true",
                                  help="Use the IteratedRadon algorithm.")
    algo_group_algos.add_argument("--tverberg", "--iterated-tverberg", "-2", action="store_true",
                                  help="Use the IteratedTverberg algorithm.")
    algo_group_algos.add_argument("--mulzer", "-3", action="store_true",
                                  help="Use the Mulzer algorithm.")

    parser.add_argument("points", nargs="?",
                        #type=argparse.FileType('r'),
                        default=sys.stdin, metavar="POINTS",
                        help="Set of points. If no argument is given the set is read from stdin. See also Input Formats.")

    format_group = parser.add_argument_group("Input format")
    format_group.add_argument("--csv", nargs="?", type=str, const="\t", default="\t",
                              metavar="SEP", help="Read from a csv file separated by SEP (default: \\t) (default).")
    format_group.add_argument("--json", action="store_true",
                              help="Read from a json file. NOT IMPLEMENTED YET.")

    args = parser.parse_args(argv)

    # Cleanup format
    if args.json:
        args.format = "json"
    else:
        args.format = "csv"

    args.separator = args.csv
    del args.json, args.csv


    return args


class Points:
    def __init__(self, points, dimension=None):
        if dimension is not None:
            self._dimension = dimension
        elif len(points) > 0:
            self._dimension = len(points[0])
        else:
            self._dimension = 0

        self._points = points

        self._validate()

    def _validate(self):
        # TODO: tests
        for point in self._points:
            if len(point) != self._dimension:
                # TODO: sinnvoller Fehler
                raise RuntimeError("Point with invalid Dimension.")

            for d in point:
                # TODO: numpy zahlenformat?
                if type(d) != float:
                    raise RuntimeError("Points have to be of type float.")

    @property
    def dimension(self):
        return self._dimension

    def list(self):
        return self._points

    def __repr__(self):
        return repr(self._points)


def read_points_csv(file, delimiter):
    reader = csv.reader(file, delimiter=delimiter)
    points = []

    for row in reader:
        point = map(float, row)  # Transform strings to floats, assuming they are . separated.
        points.append(point)

    file.close()
    return Points(points)


def read_points_json(file):
    raise NotImplementedError("JSON parser not defined yet.")


def main():

    # Initialize and parse the arguments.
    options = parse_arguments(sys.argv[1:])

    if options.format == "csv":
        pointlist = read_points_csv(options.points, options.separator)
    elif options.format == "json":
        pointlist = read_points_json(options.points)

    points = Points(pointlist)

    if options.radon:
        pass
    elif options.tverberg:
        pass
    elif options.mulzer:
        pass

    raise NotImplementedError()

if __name__ == "__main__":
    main()