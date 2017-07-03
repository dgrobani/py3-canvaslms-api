from canvas.core.courses import get_courses, get_courses_whitelisted
from canvas.core.outcome_groups import get_root_group
from canvas.core.outcomes import get_outcomes

from canvas.core.io import tada


def course_clos_list():

    terms = ['2017-1SP']
    programs = []
    synergis = True
    course_whitelist = get_courses_whitelisted([])

    for course in course_whitelist or get_courses(terms, programs, synergis):
        print(course['sis_course_id'])
        for clo in get_outcomes('courses', course['id'], get_root_group('courses', course['id'])):
            print(clo['title'])
        print()

if __name__ == '__main__':
    course_clos_list()
    tada()
