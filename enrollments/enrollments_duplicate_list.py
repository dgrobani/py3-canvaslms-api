from canvas.core import api
from canvas.core.courses import get_courses

course_whitelist = []
terms = ['2017-1SP']
programs = []
synergis = True
for course in course_whitelist or get_courses(terms, programs, synergis):
    for person in api.get_list('courses/{}/users?include[]=enrollments'.format(course['id'])):
        if len(person['enrollments']) > 1:
            for enrollment in person['enrollments']:
                print('{}\t{}\t{}\t{}'.format(course['sis_course_id'], person['name'], enrollment['role'],
                                              enrollment['created_at']))
