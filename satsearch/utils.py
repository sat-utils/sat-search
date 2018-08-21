import base64
import calendar
import collections
import logging
import os
import time


logger = logging.getLogger(__name__)


# from https://gist.github.com/angstwad/bf22d1822c38a92ec0a9#gistcomment-2622319
def dict_merge(dct, merge_dct, add_keys=True):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.

    This version will return a copy of the dictionary and leave the original
    arguments untouched.

    The optional argument ``add_keys``, determines whether keys which are
    present in ``merge_dict`` but not ``dct`` should be included in the
    new dict.

    Args:
        dct (dict) onto which the merge is executed
        merge_dct (dict): dct merged into dct
        add_keys (bool): whether to add new keys

    Returns:
        dict: updated dict
    """
    dct = dct.copy()
    if not add_keys:
        merge_dct = {
            k: merge_dct[k]
            for k in set(dct).intersection(set(merge_dct))
        }

    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dct[k] = dict_merge(dct[k], merge_dct[k], add_keys=add_keys)
        else:
            dct[k] = merge_dct[k]

    return dct


def get_s3_signed_url(url, region='eu-central-1'):
    import sys, os, base64, datetime, hashlib, hmac

    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    if access_key is None or secret_key is None:
        # if credentials not provided, just try to download without signed URL
        return url, None

    parts = url.replace('https://', '').split('/')
    bucket = parts[0].replace('.s3.amazonaws.com', '')
    key = '/'.join(parts[1:])

    service = 's3'
    host = '%s.s3-%s.amazonaws.com' % (bucket, region) #parts[0] #'s3-%s.amazonaws.com' % region
    host = '%s.s3.amazonaws.com' % (bucket)
    request_parameters = ''

    # Key derivation functions. See:
    # http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def getSignatureKey(key, dateStamp, regionName, serviceName):
        kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
        kRegion = sign(kDate, regionName)
        kService = sign(kRegion, serviceName)
        kSigning = sign(kService, 'aws4_request')
        return kSigning

    # Create a date for headers and the credential string
    t = datetime.datetime.utcnow()
    amzdate = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

    # create signed request and headers
    canonical_uri = '/' + key
    canonical_querystring = request_parameters
    payload_hash = 'UNSIGNED-PAYLOAD'
    canonical_headers = 'host:%s\nx-amz-content-sha256:%s\nx-amz-date:%s\nx-amz-request-payer:requester\n' % (host, payload_hash, amzdate)
    signed_headers = 'host;x-amz-content-sha256;x-amz-date;x-amz-request-payer'
    canonical_request = 'GET\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
    string_to_sign = algorithm + '\n' +  amzdate + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    signing_key = getSignatureKey(secret_key, datestamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
    headers = {'x-amz-date':amzdate, 'x-amz-content-sha256': payload_hash, 'Authorization':authorization_header, 'x-amz-request-payer': 'requester'}
    request_url = 'https://%s%s' % (host, canonical_uri)

    logger.debug('Request URL = ' + request_url)
    #r = requests.get(request_url, headers=headers)
    #print('Response code: %d\n' % r.status_code)
    #print(r.text)
    return request_url, headers


def get_text_calendar_dates(date1, date2, cols=3):
    """ Get array of datetimes between two dates suitable for formatting """
    """
        The return value is a list of years.
        Each year contains a list of month rows.
        Each month row contains cols months (default 3).
        Each month contains list of 6 weeks (the max possible).
        Each week contains 1 to 7 days.
        Days are datetime.date objects.
    """
    year1 = date1.year
    year2 = date2.year

    # start and end rows
    row1 = int((date1.month - 1) / cols)
    row2 = int((date2.month - 1) / cols) + 1

    # generate base calendar array
    Calendar = calendar.Calendar()
    cal = []
    for yr in range(year1, year2+1):
        ycal = Calendar.yeardatescalendar(yr, width=cols)
        if yr == year1 and yr == year2:
            ycal = ycal[row1:row2]
        elif yr == year1:
            ycal = ycal[row1:]
        elif yr == year2:
            ycal = ycal[:row2]
        cal.append(ycal)
    return cal


def get_text_calendar(dates, cols=3):
    """ Get calendar covering all dates, with provided dates colored and labeled """
    _dates = sorted(dates.keys())
    _labels = set(dates.values())
    labels = dict(zip(_labels, [str(41 + i) for i in range(0, len(_labels))]))
    cal = get_text_calendar_dates(_dates[0], _dates[-1])

    # month and day headers
    months = calendar.month_name
    days = 'Mo Tu We Th Fr Sa Su'
    hformat = '{:^20}  {:^20}  {:^20}\n'
    rformat = ' '.join(['{:>2}'] * 7) + '  '

    # create output
    col0 = '\033['
    col_end = '\033[0m'
    out = ''
    for iy, yrcal in enumerate(cal):
        out += '{:^64}\n\n'.format(_dates[0].year + iy)
        for mrow in yrcal:
            mnum = mrow[0][2][3].month
            names = [months[mnum], months[mnum+1], months[mnum+2]]
            out += hformat.format(names[0], names[1], names[2])
            out += hformat.format(days, days, days)
            for r in range(0, len(mrow[0])):
                for c in range(0, cols):
                    if len(mrow[c]) == 4:
                        mrow[c].append([''] * 7)
                    if len(mrow[c]) == 5:
                        mrow[c].append([''] * 7)
                    wk = []
                    for d in mrow[c][r]:
                        if d == '' or d.month != (mnum + c):
                            wk.append('')
                        else:
                            string = str(d.day).rjust(2, ' ')
                            if d in _dates:
                                string = '%s%sm%s%s' % (col0, labels[dates[d]], string, col_end)
                            wk.append(string)
                    out += rformat.format(*wk)
                out += '\n'
            out += '\n'
    # print labels
    for lbl, col in labels.items():
        vals = list(dates.values())
        out += '%s%sm%s (%s)%s\n' % (col0, col, lbl, vals.count(lbl), col_end)
    out += '%s total dates' % len(_dates)
    return out
