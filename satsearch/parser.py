import os
import json
import argparse
import satsearch.config as config


class SatUtilsParser(argparse.ArgumentParser):

    def __init__(self, search=True, **kwargs):
        """ Initialize a SatUtilsParser """
        dhf = argparse.ArgumentDefaultsHelpFormatter
        super(SatUtilsParser, self).__init__(formatter_class=dhf, **kwargs)
        if search:
            self.add_search_args()

    def parse_args(self, *args, **kwargs):
        """ Parse arguments """
        args = super(SatUtilsParser, self).parse_args(*args, **kwargs)
        args = vars(args)
        args = {k: v for k, v in args.items() if v is not None}
        if 'date' in args:
            dt = args.pop('date').split(',')
            if len(dt) > 2:
                raise ValueError('Provide date range as single date or comma separated begin/end dates')
            if len(dt) == 1:
                dt = (dt[0], dt[0])
            args['date_from'] = dt[0]
            args['date_to'] = dt[1]

        if 'clouds' in args:
            cov = args.pop('clouds').split(',')
            if len(cov) != 2:
                raise ValueError('Provide cloud coverage range as two comma separated numbers (e.g., 0,20)')
            args['cloud_from'] = int(cov[0])
            args['cloud_to'] = int(cov[1])

        if 'intersects' in args:
            if os.path.exists(args['intersects']):
                with open(args['intersects']) as f:
                    args['intersects'] = json.dumps(json.loads(f.read()))

        # set global configuration options
        if 'datadir' in args:
            config.DATADIR = args.pop('datadir')
        if 'nosubdirs' in args:
            config.NOSUBDIRS = args.pop('nosubdirs')

        return args

    def add_search_args(self):
        """ Adds search arguments to a parser """
        parser = self
        group = parser.add_argument_group('search parameters')
        group.add_argument('--satellite_name')
        group.add_argument('--scene_id', help='One or more scene IDs', nargs='*', default=None)
        group.add_argument('--intersects', help='GeoJSON Feature (file or string)')
        group.add_argument('--contains', help='lon,lat points')
        #group.add_argument('--sensor')
        group.add_argument('--date', help='Single date or begin and end date (e.g., 2017-01-01,2017-02-15')
        group.add_argument('--clouds', help='Range of acceptable cloud cover (e.g., 0,20)')
        group.add_argument('--param', nargs='*', help='Additional parameters of form KEY=VALUE', action=self.KeyValuePair)

        group = parser.add_argument_group('sat-utils data files')
        group.add_argument('--datadir', help='Local directory to save images', default=config.DATADIR)
        group.add_argument('--nosubdirs', help='When saving, do not create directories usng scene_id',
                           default=False, action='store_true')
        group.add_argument('--download', help='Download files', default=None, nargs='*')
        group.add_argument('--source', help='Download source', default='aws_s3')

        group = parser.add_argument_group('search output')
        group.add_argument('--printmd', help='Print specified metadata for matched scenes', default=None, nargs='*')
        group.add_argument('--printcal', help='Print calendar showing dates', default=False, action='store_true')
        group.add_argument('--review', help='Interactive review of thumbnails', default=False, action='store_true')
        group.add_argument('--save', help='Save scenes metadata as GeoJSON', default=None)

        return parser

    class KeyValuePair(argparse.Action):
        """ Custom action for getting arbitrary key values from argparse """
        def __call__(self, parser, namespace, values, option_string=None):
            for val in values:
                n, v = val.split('=')
                setattr(namespace, n, v)
