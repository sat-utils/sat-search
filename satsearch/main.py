import os
import sys
import json
from .version import __version__
from satsearch import Search
from satstac import Items
from satsearch.parser import SatUtilsParser


def main(items=None, print_md=None, print_cal=False,
         save=None, download=None, **kwargs):
    """ Main function for performing a search """
    if items is None:
        # get items from search
        search = Search(**kwargs)
        items = search.items()
    else:
        items = Items.load(items)

    # print metadata
    if print_md is not None:
        items.print_summary(print_md)

    # print calendar
    if print_cal:
        print(items.text_calendar())

    # save all metadata in JSON file
    if save is not None:
        items.save(filename=save)

    print('%s items found' % len(items))

    # download files given keys
    if download is not None:
        for key in download:
            items.download(key=key)

    return items


def cli():
    parser = SatUtilsParser.newbie(description='sat-search (v%s)' % __version__)
    args = parser.parse_args(sys.argv[1:])

    # read the GeoJSON file
    if 'intersects' in args:
        if os.path.exists(args['intersects']):
            with open(args['intersects']) as f:
                args['intersects'] = json.dumps(json.loads(f.read()))

    cmd = args.pop('command', None)
    if cmd is not None:
        return main(**args)


if __name__ == "__main__":
    cli()
