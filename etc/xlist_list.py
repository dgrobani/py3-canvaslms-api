from canvas.core.courses import get_course_sections, get_course, get_courses

from canvas.core.io import tada


course_whitelist = []
terms = ['2017-3FA']
programs = ['OT']
synergis = False

for course in get_courses(terms, programs, synergis, course_whitelist):
    # rolled back code golf:
    # for xlist in sorted([get_course(section['nonxlist_course_id'])['sis_course_id']
    #                      for section in get_course_sections(course['id']) if section['nonxlist_course_id']]):
    #     print('{:<40} -->  {}'.format(xlist, course['course_sis_id']))
    for section in get_course_sections(course['id']):
        if section['nonxlist_course_id']:
            xlist = get_course(section['nonxlist_course_id'])['sis_course_id']
            print('{:<40} -->  {}'.format(xlist, course['sis_course_id']))

tada()
