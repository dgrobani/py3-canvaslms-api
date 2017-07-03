from canvas.core.courses import get_courses
import canvas.core.api as api


terms = ['2017-2SU']
programs = ['NFNPO', 'NCMO']
synergis = True

for course in get_courses(terms, programs, synergis, []):
    print(course['sis_course_id'])
    req_data = {'course[end_at]': '2017-08-21T23:59:59-07:00', 'course[restrict_enrollments_to_course_dates]': False}
    api.put('courses/{}/'.format(course['id']), req_data)
