from datetime import datetime

from canvas.core.courses import get_courses, get_courses_whitelisted, get_course_people
from canvas.core.io import write_xlsx_file, tada

from canvas.core.assignments import get_assignments

assignment_qtys = {}
terms = ['2017-1SP']
programs = []
synergis = True
course_whitelist = get_courses_whitelisted([])

for course in course_whitelist or get_courses(terms, programs, synergis):
    course_id = course['id']
    if not get_course_people(course_id, 'student'):
        continue
    for assignment in get_assignments(course_id):
        if (assignment.get('turnitin_enabled', False)) or \
                ('external_tool' in assignment['submission_types'] and
                 'turnitin' in (assignment['external_tool_tag_attributes']['url'] or '')):
            key = '{}|{}|{}'.format(terms[0], course['course_sis_info']['program'],
                                    ' & '.join([p['name'] for p in get_course_people(course_id, 'Faculty of record')]))
            assignment_qtys[key] = assignment_qtys.get(key, 0) + 1
            print(key)

header = ['term', 'program', 'faculty', '# of TII assignments']
rows = [key.split('|') + [assignment_qtys[key]] for key in assignment_qtys]
write_xlsx_file('turnitin_assignments_by_faculty_spring_{}'
                .format(datetime.now().strftime('%Y.%m.%d.%H.%M.%S')), header, rows)
tada()
