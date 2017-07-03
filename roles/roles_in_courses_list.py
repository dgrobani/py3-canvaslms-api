from canvas.core.courses import get_courses, get_course_people

from canvas.core.io import tada


def find_courses_for_role():
    terms = ['2016-2SU']
    programs = ['NFNPO']
    role = 'Teacher Read-Only'

    print(role)
    course_whitelist = []
    synergis = False
    for course in course_whitelist or get_courses(terms, programs, synergis):
        people = get_course_people(course['id'], role)
        if 'errors' not in people:
            for person in people:
                print(course['sis_course_id'], person['name'])

if __name__ == '__main__':
    find_courses_for_role()
    tada()
