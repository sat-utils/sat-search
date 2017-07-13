import os
import sys
import argparse
import logging
import json
import datetime
from .version import __version__
from satsearch import Search

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

    group = parser.add_argument_group('Spatial')
    group.add_argument('--intersects', help='GeoJSON Feature (file or string)')
    group.add_argument('--contains', help='long,lat points')

    group = parser.add_argument_group('Quality')
    group.add_argument('--cloud_from', help='Lower limit for cloud coverage')
    group.add_argument('--cloud_to', help='Upper limit for cloud coverage')

    args = vars(parser.parse_args(args))
    args = {k: v for k, v in args.items() if v is not None}

    if 'intersects' in args:
        if os.path.exists(args['intersects']):
            with open(args['intersects']) as f:
                args['intersects'] = json.dumps(json.loads(f.read()))

    return args


def monthlist(dates):
    start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in dates]
    total_months = lambda dt: dt.month + 12 * dt.year
    mlist = []
    for tot_m in xrange(total_months(start)-1, total_months(end)):
        y, m = divmod(tot_m, 12)
        mlist.append(datetime(y, m+1, 1).strftime("%b-%y"))
    return mlist


def main(*args, **kwargs):
    """ Main function for performing a search """
    print('Searching for scenes matching criteria:')
    for kw in kwargs:
        print('  %s: %s' % (kw, kwargs[kw]))

    search = Search(**kwargs)

    print('Found %s matching scenes' % search.found())

    scenes = search.scenes()

    dates = search.scene_dates()

    return scenes


def cli():
    args = parse_args(sys.argv[1:])
    main(**args)


if __name__ == "__main__":
    cli()
