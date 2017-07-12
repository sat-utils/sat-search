import sys
import argparse
import logging
from .version import __version__

logger = logging.getLogger(__name__)


def parse_args(args):
    """ Parse arguments for sat-search CLI """
    desc = 'sat-search (v%s)' % __version__
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)

    return parser.parse_args(args)


def main():
    """ Main function for performing a search """
    logger.warning("Not yet implemented")


def cli():
    args = parse_args(sys.argv[1:])
    main(**args)


if __name__ == "__main__":
    cli()
