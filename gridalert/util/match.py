import re

from . import date  as util_date

def re_list(target, patterns):
    match = False

    for pattern in patterns:
        if re.match(pattern, target):
            match = True

    return match


def base_match(conf, host, date):
    match1 = re_list(host, conf.hosts)
    match2 = util_date.in_sqdate('%s' % date,
                                 conf.date_start,
                                 conf.date_end)

    return match1 and match2
 
