from canvas.core.courses import get_courses
from canvas.core.io import tada

from canvas.core.assignments import get_assignments

programs = ['NFNPO']
terms = ['2017-1SP']
synergis = True

for course in get_courses(terms, programs, synergis):
    for assignment in get_assignments(course['id']):
        if 'external_tool' in assignment['submission_types']:
            print(course['sis_course_id'], assignment['external_tool_tag_attributes']['url'], assignment['name'])

tada()
