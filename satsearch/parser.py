import os
import sys
import logging
import argparse
import satsearch.config as config
from .version import __version__


class SatUtilsParser(argparse.ArgumentParser):

    def __init__(self, **kwargs):
        """ Initialize a SatUtilsParser """
        super(SatUtilsParser, self).__init__(**kwargs)
        self.formatter_class = argparse.ArgumentDefaultsHelpFormatter

        self.pparser = argparse.ArgumentParser(add_help=False)
        self.pparser.add_argument('--version', help='Print version and exit', action='version', version=__version__)
        self.pparser.add_argument('-v', '--verbosity', default=2, type=int,
                            help='0:quiet, 1:error, 2:warning, 3:info, 4:debug')
        self.subparser = None

    def parse_args(self, *args, **kwargs):
        """ Parse arguments """
        args = super(SatUtilsParser, self).parse_args(*args, **kwargs)
        args = vars(args)
        args = {k: v for k, v in args.items() if v is not None}

        if args.get('command', None) is None:
            self.print_help()
            sys.exit(0)

        # set logging level
        if 'verbosity' in args:
            logging.basicConfig(stream=sys.stdout, level=(50-args.pop('verbosity') * 10))

        # set global configuration options
        if 'url' in args:
            config.API_URL = args.pop('url')
        if 'datadir' in args:
            config.DATADIR = args.pop('datadir')
        if 'filename' in args:
            config.FILENAME = args.pop('filename')

        return args

    def add_subparser(self, *args, parents=[], **kwargs):
        if not self.subparser:
            self.subparser = self.add_subparsers(dest='command')
        parents.append(self.pparser)
        subparser = self.subparser.add_parser(*args, parents=parents, **kwargs)
        return subparser

    def add_collections_parser(self):
        """ Add parser for collections """
        subparser = self.add_subparser('collections', help='Collections API', download=False, output=False)
        group = subparser.add_argument_group('collection parameters')
        group.add_argument('-c', '--collection', help='Name of collection')

    def add_search_parser(self, download=True, output=True):
        parents = []
        if download:
            parents.append(self.get_download_parser())
        if output:
            parents.append(self.get_output_parser())
        subparser = self.add_subparser('search', help='Search API', parents=parents)
        """ Adds search arguments to a parser """
        group = subparser.add_argument_group('search parameters')
        group.add_argument('-c', '--c:id', help='Name of collection')
        group.add_argument('--intersects', help='GeoJSON Feature (file or string)')
        #group.add_argument('--id', help='One or more scene IDs', nargs='*', default=None)
        #group.add_argument('--contains', help='lon,lat points')
        group.add_argument('--datetime', help='Single date/time or begin and end date/time (e.g., 2017-01-01/2017-02-15')
        group.add_argument('--eo:cloud_cover', help='Range of acceptable cloud cover (e.g., 0/20)')
        group.add_argument('-p', '--param', nargs='*', help='Additional parameters of form KEY=VALUE', action=SatUtilsParser.KeyValuePair)
        group.add_argument('--url', help='URL of the API', default=config.API_URL)

    def add_load_parser(self, download=True, output=True):
        parents = []
        if download:
            parents.append(self.get_download_parser())
        if output:
            parents.append(self.get_output_parser())
        subparser = self.add_subparser('load', help='Load scenes from file')
        subparser.add_argument('scenes', help='GeoJSON file of scenes')

    def get_download_parser(self):
        parser = argparse.ArgumentParser(add_help=False)
        group = parser.add_argument_group('download parameters')
        group.add_argument('--datadir', help='Directory pattern to save assets', default=config.DATADIR)
        group.add_argument('--filename', default=config.FILENAME,
                           help='Save assets with this filename pattern based on metadata keys')
        group.add_argument('--download', help='Download assets', default=None, nargs='*')
        return parser

    def get_output_parser(self):
        """ Add arguments for printing output """
        parser = argparse.ArgumentParser(add_help=False)
        group = parser.add_argument_group('search output')
        group.add_argument('--print_md', help='Print specified metadata for matched scenes', default=None, nargs='*')
        group.add_argument('--print_cal', help='Print calendar showing dates', default=False, action='store_true')
        group.add_argument('--save', help='Save results as GeoJSON', default=None)
        h = 'Append scenes to GeoJSON file (specified by save)'
        group.add_argument('--append', default=False, action='store_true', help=h)
        if os.getenv('IMGCAT', None):
            group.add_argument('--review', help='Interactive review of thumbnails', default=False, action='store_true')
        return parser

    class KeyValuePair(argparse.Action):
        """ Custom action for getting arbitrary key values from argparse """
        def __call__(self, parser, namespace, values, option_string=None):
            for val in values:
                n, v = val.split('=')
                setattr(namespace, n, v)
