from sortedcontainers import SortedDict

import canvas.core.api as api
from canvas.core import config


def term_data():
    return SortedDict({
        'DEFAULT': 286,
        '2012-3FA': 2909,
        '2013-1SP': 4514, '2013-2SU': 4515, '2013-3FA': 4854,
        '2014-1SP': 5180, '2014-2SU': 5489, '2014-3FA': 5562,
        '2015-1SP': 6423, '2015-2SU': 6864, '2015-3FA': 6921,
        '2016-1SP': 7518, '2016-2SU': 10200, '2016-3FA': 10398,
        '2017-1SP': 10815, '2017-2SU': 11023, '2017-3FA': 11299,
    })


def term_id_from_name(term_name):
    """ return the id for a term name """
    return term_data()[term_name]


def all_terms():
    return [term for term in term_data() if term != 'DEFAULT']


def get_canvas_terms():
    return api.get('accounts/{}/terms?per_page=100'.format(config.root_account)).json()['enrollment_terms']
