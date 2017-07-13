import os
import sys
import argparse
import logging
import json
from .version import __version__
from satsearch import Search, Scenes

logger = logging.getLogger(__name__)


def parse_args(args):
    """ Parse arguments for sat-search CLI """
    desc = 'sat-search (v%s)' % __version__
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)

    group = parser.add_argument_group('Platform')
    group.add_argument('--satellite_name')
    group.add_argument('--sensor')

    group = parser.add_argument_group('Temporal')
    group.add_argument('--date')
    group.add_argument('--date_from')
    group.add_argument('--date_to')

    group = parser.add_argument_group('Spatial')
    group.add_argument('--intersects', help='GeoJSON Feature (file or string)')
    group.add_argument('--contains', help='long,lat points')

    group = parser.add_argument_group('Quality')
    group.add_argument('--cloud_from', help='Lower limit for cloud coverage')
    group.add_argument('--cloud_to', help='Upper limit for cloud coverage')

    group = parser.add_argument_group('Output')
    group.add_argument('--printsum', help='Print basic metadata for matched scenes', default=False, action='store_true')
    group.add_argument('--printcal', help='Print calendar showing dates', default=False, action='store_true')
    group.add_argument('--save', help='Save Scenes as file', default=None)

    args = vars(parser.parse_args(args))
    args = {k: v for k, v in args.items() if v is not None}

    if 'intersects' in args:
        if os.path.exists(args['intersects']):
            with open(args['intersects']) as f:
                args['intersects'] = json.dumps(json.loads(f.read()))

    return args


def main(*args, **kwargs):
    """ Main function for performing a search """
    # arguments that aren't not search parameters
    printsum = kwargs.pop('printsum', False)
    printcal = kwargs.pop('printcal', False)
    save = kwargs.pop('save', None)

    print('Searching for scenes matching criteria:')
    for kw in kwargs:
        print('  %s: %s' % (kw, kwargs[kw]))

    search = Search(**kwargs)

    print('Found %s matching scenes' % search.found())

    scenes = Scenes(search.scenes())

    if printsum:
        scenes.print_summary()

    if printcal:
        scenes.print_calendar()

    if save is not None:
        scenes.save(filename=save)

    return scenes


def cli():
    args = parse_args(sys.argv[1:])
    scenes = main(**args)
    return len(scenes)


if __name__ == "__main__":
    cli()
