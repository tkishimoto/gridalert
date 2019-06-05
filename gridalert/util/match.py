import re

from . import date  as util_date

def re_list(target, patterns):
    match = False

    for pattern in patterns:
        if re.match(pattern, target):
            match = True

    return match


def base_match(cl_conf, cluster, host, date):
    match1 = re_list(host, cl_conf['hosts'].split(','))
    match2 = util_date.in_sqdate('%s' % date,
                                 cl_conf['date_start'],
                                 cl_conf['date_end'])

    match3 = (cl_conf['name'] == cluster)

    return match1 and match2 and match3


def base_match_wo_cluster(cl_conf, host, date):
    match1 = re_list(host, cl_conf['hosts'].split(','))
    match2 = util_date.in_sqdate('%s' % date,
                                 cl_conf['date_start'],
                                 cl_conf['date_end'])

    return match1 and match2
