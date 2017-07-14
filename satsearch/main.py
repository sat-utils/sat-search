import os
import sys
import argparse
import logging
import json
from .version import __version__
from satsearch import Search, Scenes
import satsearch.config as config

logger = logging.getLogger(__name__)


class KeyValuePair(argparse.Action):
    """ Custom action for getting arbitrary key values from argparse """
    def __call__(self, parser, namespace, values, option_string=None):
        for val in values:
            n, v = val.split('=')
            setattr(namespace, n, v)


def parse_args(args):
    """ Parse arguments for sat-search CLI """
    desc = 'sat-search (v%s)' % __version__
    dhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=desc, formatter_class=dhf)

    group = parser.add_argument_group('Platform search parameters')
    group.add_argument('--satellite_name')
    group.add_argument('--sensor')

    group = parser.add_argument_group('Temporal search parameters')
    group.add_argument('--date')
    group.add_argument('--date_from')
    group.add_argument('--date_to')

    group = parser.add_argument_group('Spatial search parameters')
    group.add_argument('--intersects', help='GeoJSON Feature (file or string)')
    group.add_argument('--contains', help='long,lat points')

    group = parser.add_argument_group('Other search parameters')
    group.add_argument('--scene_id', help='One or more scene IDs', nargs='*', default=None)
    group.add_argument('--cloud_from', help='Lower limit for cloud coverage')
    group.add_argument('--cloud_to', help='Upper limit for cloud coverage')
    group.add_argument('--param', nargs='*', help='Additional parameters of form KEY=VALUE', action=KeyValuePair)

    group = parser.add_argument_group('Output')
    group.add_argument('--printsum', help='Print basic metadata for matched scenes', default=False, action='store_true')
    group.add_argument('--printcal', help='Print calendar showing dates', default=False, action='store_true')
    group.add_argument('--save', help='Save metadata of all scenes as file', default=None)
    group.add_argument('--datadir', help='Local directory to save images', default=config.DATADIR)
    group.add_argument('--nosubdirs', help='When saving, do not create directories usng scene_id',
                       default=False, action='store_true')

    group = parser.add_argument_group('Download')
    group.add_argument('--dlthumbs', help='Download thumbnails', default=False, action='store_true')
    group.add_argument('--dlfiles', help='Download files', default=None, nargs='*')

    args = vars(parser.parse_args(args))
    args = {k: v for k, v in args.items() if v is not None}

    if 'intersects' in args:
        if os.path.exists(args['intersects']):
            with open(args['intersects']) as f:
                args['intersects'] = json.dumps(json.loads(f.read()))

    return args


def main(datadir=config.DATADIR, nosubdirs=config.NOSUBDIRS, printsum=False, printcal=False,
         save=None, dlthumbs=None, dlfiles=None, **kwargs):
    """ Main function for performing a search """
    config.DATADIR = datadir
    config.NOSUBDIRS = nosubdirs

    print('Searching for scenes matching criteria:')
    for kw in kwargs:
        print('  %s: %s' % (kw, kwargs[kw]))

    search = Search(**kwargs)

    print('Found %s matching scenes' % search.found())

    # create Scenes collection
    scenes = Scenes(search.scenes())

    # print summary
    if printsum:
        scenes.print_summary()

    # print calendar
    if printcal:
        scenes.print_calendar()

    # save all metadata in JSON file
    if save is not None:
        scenes.save(filename=save)

    # download all thumbnails
    if dlthumbs:
        scenes.download_thumbnails(path=datadir, nosubdirs=nosubdirs)

    # download files given keys
    if dlfiles is not None:
        for key in dlfiles:
            scenes.download(key=key, path=datadir, nosubdirs=nosubdirs)

    return scenes


def cli():
    args = parse_args(sys.argv[1:])
    scenes = main(**args)
    return len(scenes)


if __name__ == "__main__":
    cli()
