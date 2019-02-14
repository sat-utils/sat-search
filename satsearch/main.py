import os
import sys
import json
from .version import __version__
from satsearch import Search
from satstac import Items
from satsearch.parser import SatUtilsParser

import satsearch.config as config


def main(items=None, printmd=None, printcal=False, found=False,
         save=None, download=None, requestor_pays=False, **kwargs):
    """ Main function for performing a search """
    
    if items is None:
        ## if there are no items then perform a search
        search = Search.search(**kwargs)
        if found:
            num = search.found()
            print('%s items found' % num)
            return num
        items = search.items()
    else:
        # otherwise, load a search from a file
        items = Items.load(items)

    print('%s items found' % len(items))

    # print metadata
    if printmd is not None:
        print(items.summary(printmd))

    # print calendar
    if printcal:
        print(items.calendar())

    # save all metadata in JSON file
    if save is not None:
        items.save(filename=save)

    # download files given `download` keys
    if download is not None:
        if 'ALL' in download:
            # get complete set of assets
            download = set([k for i in items for k in i.assets])
        for key in download:
            items.download(key=key, path=config.DATADIR, filename=config.FILENAME, requestor_pays=requestor_pays)

    return items


def cli():
    parser = SatUtilsParser.newbie(description='sat-search (v%s)' % __version__)
    kwargs = parser.parse_args(sys.argv[1:])

    # if a filename, read the GeoJSON file
    if 'intersects' in kwargs:
        if os.path.exists(kwargs['intersects']):
            with open(kwargs['intersects']) as f:
                kwargs['intersects'] = json.loads(f.read())

    cmd = kwargs.pop('command', None)
    if cmd is not None:
        main(**kwargs)


if __name__ == "__main__":
    cli()
