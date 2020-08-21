import argparse
import json
import logging
import os
import sys

from .version import __version__
from satsearch import Search
from satstac import ItemCollection
from satstac.utils import dict_merge

API_URL = os.getenv('STAC_API_URL', None)


class SatUtilsParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        """ Initialize a SatUtilsParser """
        super(SatUtilsParser, self).__init__(*args, **kwargs)
        self.formatter_class = argparse.ArgumentDefaultsHelpFormatter

        self.pparser = argparse.ArgumentParser(add_help=False)
        self.pparser.add_argument('--version', help='Print version and exit', action='version', version=__version__)
        self.pparser.add_argument('-v', '--verbosity', default=2, type=int,
                            help='0:quiet, 1:error, 2:warning, 3:info, 4:debug')

        self.download_parser = argparse.ArgumentParser(add_help=False)
        self.download_group = self.download_parser.add_argument_group('download options')
        self.download_group.add_argument('--filename_template', default='${collection}/${date}/${id}',
                           help='Save assets with this filename pattern based on metadata keys')
        self.download_group.add_argument('--download', help='Download assets', default=None, nargs='*')
        h = 'Acknowledge paying egress costs for downloads (if in requester pays bucket on AWS)'
        self.download_group.add_argument('--requester-pays', help=h, default=False, action='store_true', dest='requester_pays')

        self.output_parser = argparse.ArgumentParser(add_help=False)
        self.output_group = self.output_parser.add_argument_group('output options')
        h = 'Print specified metadata for matched scenes'
        self.output_group.add_argument('--print-md', help=h, default=None, nargs='*', dest='printmd')
        h = 'Print calendar showing dates'
        self.output_group.add_argument('--print-cal', help=h, dest='printcal')
        self.output_group.add_argument('--save', help='Save results as GeoJSON', default=None)

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

        # if a filename, read the GeoJSON file
        if 'intersects' in args:
            if os.path.exists(args['intersects']):
                with open(args['intersects']) as f:
                    data = json.loads(f.read())
                    if data['type'] == 'Feature':
                        args['intersects'] = data['geometry']
                    elif data['type'] == 'FeatureCollection':
                        args['intersects'] = data['features'][0]['geometry']
                    else:
                        args['intersects'] = data

        # If a filename, read the JSON file
        if 'headers' in args:
            if os.path.exists(args['headers']):
                with open(args['headers']) as f:
                    headers = json.loads(f.read())
            else:
                headers = json.loads(args['headers'])
            args['headers'] = {k: str(v) for k,v in headers.items()}

        return args

    @classmethod
    def newbie(cls, *args, **kwargs):
        """ Create a newbie class, with all the skills needed """
        parser = cls(*args, **kwargs)
        subparser = parser.add_subparsers(dest='command')
        parents = [parser.pparser, parser.output_parser]

        sparser = subparser.add_parser('search', help='Perform new search of items', parents=parents)
        """ Adds search arguments to a parser """
        parser.search_group = sparser.add_argument_group('search options')
        parser.search_group.add_argument('-c', '--collections', help='Name of collection', nargs='*')
        h = 'One or more scene IDs from provided collection (ignores other parameters)'
        parser.search_group.add_argument('--ids', help=h, nargs='*', default=None)
        parser.search_group.add_argument('--bbox', help='Bounding box (min lon, min lat, max lon, max lat)', nargs=4)
        parser.search_group.add_argument('--intersects', help='GeoJSON Feature (file or string)')
        parser.search_group.add_argument('--datetime', help='Single date/time or begin and end date/time (e.g., 2017-01-01/2017-02-15)')
        parser.search_group.add_argument('-q', '--query', nargs='*', help='Query properties of form KEY=VALUE (<, >, <=, >=, = supported)')
        parser.search_group.add_argument('--sortby', help='Sort by fields', nargs='*')
        h = 'Only output how many Items found'
        parser.search_group.add_argument('--found', help=h, action='store_true', default=False)
        parser.search_group.add_argument('--url', help='URL of the API', default=API_URL)
        parser.search_group.add_argument('--headers', help='Additional request headers (JSON file or string)', default=None)
        parser.search_group.add_argument('--limit', help='Limits the total number of items returned', default=None)

        parents.append(parser.download_parser)
        lparser = subparser.add_parser('load', help='Load items from previous search', parents=parents)
        lparser.add_argument('items', help='GeoJSON file of Items')
        return parser

    class KeyValuePair(argparse.Action):
        """ Custom action for getting arbitrary key values from argparse """
        def __call__(self, parser, namespace, values, option_string=None):
            for val in values:
                n, v = val.split('=')
                setattr(namespace, n, {'eq': v})


def main(items=None, printmd=None, printcal=None,
         found=False, filename_template='${collection}/${date}/${id}',
         save=None, download=None, requester_pays=False, headers=None, **kwargs):
    """ Main function for performing a search """
    
    if items is None:
        ## if there are no items then perform a search
        search = Search.search(headers=headers, **kwargs)
        ## Commenting out found logic until functions correctly.
        if found:
             num = search.found(headers=headers)
             print('%s items found' % num)
             return num
        items = search.items(headers=headers)
    else:
        # otherwise, load a search from a file
        items = ItemCollection.open(items)

    print('%s items found' % len(items))

    # print metadata
    if printmd is not None:
        print(items.summary(printmd))

    # print calendar
    if printcal:
        print(items.calendar(printcal))

    # save all metadata in JSON file
    if save is not None:
        items.save(filename=save)

    # download files given `download` keys
    if download is not None:
        if 'ALL' in download:
            # get complete set of assets
            download = set([k for i in items for k in i.assets])
        for key in download:
            items.download(key=key, filename_template=filename_template, requester_pays=requester_pays)

    return items


def cli():
    parser = SatUtilsParser.newbie(description='sat-search (v%s)' % __version__)
    kwargs = parser.parse_args(sys.argv[1:])

    cmd = kwargs.pop('command', None)
    if cmd is not None:
        main(**kwargs)


if __name__ == "__main__":
    cli()
