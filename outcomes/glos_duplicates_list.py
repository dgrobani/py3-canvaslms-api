from canvas.core.accounts import program_account, all_programs
from canvas.core.constants import all_programs, term_id_from_name
from canvas.core.courses import get_courses, validate_course
from canvas.core.outcome_groups import get_root_group
from canvas.core.outcomes import get_outcomes
from canvas.core.utility import make_leader

from canvas.core.io import tada


def list_duplicate_glos():

    programs = ['BSN', 'DNP']
    term = '2015FALL'
    term_id = term_id(term)
    for program in programs or all_programs('fnp_online_yes'):
        print(program, '-' * 70)
        account = program_account(program)
        for course in get_courses(account, term_id):
            if not validate_course(course, program):
                continue
            leader = make_leader(program, course['sis_course_id'])
            glos = []
            for clo in get_outcomes('courses', course['id'], get_root_group('courses', course['id'])):
                if 'Genomics' in clo['title']:
                    if clo['title'] in glos:
                        print(leader, clo['title'])
                    else:
                        glos.append(clo['title'])


if __name__ == '__main__':
    list_duplicate_glos()
    tada()
