from sortedcontainers import SortedDict

from canvas.core.api import get_list


def get_subaccounts(account_id):
    return sorted(get_list('accounts/{}/sub_accounts'.format(account_id)), key=lambda s: s['name'])


def get_admins(account_id):
    return sorted(get_list('accounts/{}/admins'.format(account_id)), key=lambda a: (a['role'], a['user']['name']))


def get_roles(account_id):
    return get_list('accounts/{}/roles'.format(account_id))


def get_account_grading_standard(account_id):
    """ return an account's grading standard(s?) """
    return get_list('accounts/{}/grading_standards'.format(account_id))


def program_data():
    return SortedDict({
        # account, cmi, synergis, catalog, title
        'BSCI': ['98327', 'BSCI', 'N', 'BSCI', 'Basic Sciences'],
        'NABSN': ['98340', 'ABSN', 'N', 'NURSG', 'Accelerated Bachelor of Science in Nursing'],
        'NBSN': ['98339', 'BSN', 'N', 'NURSG', 'Bachelor of Science in Nursing'],
        'NCM': ['98332', 'MSN_CM', 'N', 'NURSG', 'Master of Science in Nursing: Case Management'],
        'NCMO': ['145593', 'MSN_CM', 'Y', 'NURSG', 'Master of Science in Nursing: Case Management (Online)'],
        'NCRNA': ['98334', 'MSN_CRNA', 'N', 'NURSG', 'Master of Science in Nursing: CRNA'],
        'NDNP': ['98330', 'DNP', 'N', 'NURSG', 'Doctor of Nursing Practice'],
        'NELMSN': ['98335', 'ELMSN', 'N', 'NURSG', 'Entry Level Master of Science in Nursing'],
        'NFNP': ['98333', 'MSN_FNP', 'N', 'NURSG', 'Master of Science in Nursing: Family Nurse Practitioner'],
        'NFNPO': ['145067', 'MSN_FNP', 'Y', 'NURSG', 'Master of Science in Nursing: Family Nurse Practitioner (Online)'],
        'NR2B': ['167901', 'RN2BSN', 'N', 'NURSG', 'RN to BSN'],
        'OT': ['98323', 'MOT', 'N', 'OCCTH', 'Doctor of Occupational Therapy'],
        'PA': ['98324', 'MPA', 'N', 'PA', 'Master of Science in Physician Assistant'],
        'PM': ['98325', 'DPM', 'N', 'PM', 'Doctor of Podiatric Medicine'],
        'PT': ['98326', 'DPT', 'N', 'PHYTH', 'Doctor of Physical Therapy']
    })


def program_account(program):
    return program_data().get(program, [program])[0]


def cmi_program(program):
    return program_data()[program][1]


def catalog_program(program):
    return program_data()[program][3]


def program_formal_name(program):
    return program_data()[program][4]


def all_programs(synergis):
    programs = program_data()
    return [program for program in programs if synergis or programs[program][2] == 'N']
