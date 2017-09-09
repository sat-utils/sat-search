import os
import sys
import json
from .version import __version__
from satsearch import Search, Scenes
from satsearch.parser import SatUtilsParser


def main(review=False, printmd=None, printcal=False,
         save=None, download=None, source='aws_s3', **kwargs):
    """ Main function for performing a search """
    txt = 'Search for scenes matching criteria:\n'
    for kw in kwargs:
        if kw == 'intersects':
            geom = json.dumps(json.loads(kwargs[kw])['geometry'])
            txt += ('{:>20}: {:<40} ...\n'.format(kw, geom[0:70]))
        else:
            txt += ('{:>20}: {:<40}\n'.format(kw, kwargs[kw]))
    print(txt)

    # get scenes from search
    search = Search(**kwargs)
    scenes = Scenes(search.scenes())

    print('Found %s matching scenes' % len(scenes))

    if review:
        if not os.getenv('IMGCAT', None):
            raise ValueError('Set IMGCAT envvar to terminal image display program to use review feature')
        scenes.review_thumbnails()

    # print summary
    if printmd is not None:
        scenes.print_scenes(printmd)

    # print calendar
    if printcal:
        print(scenes.text_calendar())

    # save all metadata in JSON file
    if save is not None:
        scenes.save(filename=save)

    # download files given keys
    if download is not None:
        for key in download:
            scenes.download(key=key, source=source)

    return scenes


def cli():
    parser = SatUtilsParser(description='sat-search (v%s)' % __version__)
    args = parser.parse_args(sys.argv[1:])
    scenes = main(**args)
    return len(scenes)


if __name__ == "__main__":
    cli()
