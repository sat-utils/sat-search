import os
import sys
import json
from .version import __version__
from satsearch import Search, Scenes
from satsearch.parser import SatUtilsParser


def main(scenes=None, print_md=None, print_cal=False,
         save=None, download=None, **kwargs):
    """ Main function for performing a search """
    if scenes is None:
        # get scenes from search
        search = Search(**kwargs)
        scenes = Scenes(search.scenes(), properties=kwargs)
    else:
        scenes = Scenes.load(scenes)

    # print metadata
    if print_md is not None:
        scenes.print_scenes(print_md)

    # print calendar
    if print_cal:
        print(scenes.text_calendar())

    # save all metadata in JSON file
    if save is not None:
        scenes.save(filename=save)

    print('%s scenes found' % len(scenes))

    # download files given keys
    if download is not None:
        for key in download:
            scenes.download(key=key)

    return scenes


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
        main(**args)


if __name__ == "__main__":
    cli()
