import calendar


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
    #from nose.tools import set_trace; set_trace()
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
