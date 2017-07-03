# https://canvas.instructure.com/doc/api/assignments.html
from datetime import datetime

from canvas.core.courses import get_courses, get_course_people
from canvas.core.io import write_xlsx_file, tada

from canvas.core.assignments import get_assignments


def turnitin_api_assignments():
    terms = ['2017-2SU']
    programs = []
    synergis = True
    course_whitelist = []
    header = ['term', 'program', 'SIS ID', 'assignment name', 'assignment URL', 'due date', 'submission types',
              'points', 'rubric with grading criteria', 'rubric with CLOs', 'group assignment', 'faculty of record']
    rows = []

    for course in get_courses(terms, programs, synergis, course_whitelist):
        course_id = course['id']
        course_sis_id = course['sis_course_id']
        program = course['course_sis_info']['program']
        for assignment in get_assignments(course_id):
            if 'turnitin_enabled' in assignment and assignment['turnitin_enabled'] \
                    and 'external_tool' not in assignment['submission_types']:
                rubric_has_criteria = ''
                rubric_has_clos = ''
                if 'rubric' in assignment:
                    for criterion in assignment['rubric']:
                        if 'outcome_id' in criterion:
                            rubric_has_clos = 'X'
                        if 'id' in criterion:
                            rubric_has_criteria = 'X'
                row = [terms[0],
                       program,
                       course_sis_id,
                       assignment['name'],
                       assignment['html_url'],
                       assignment['due_at'][0:10] if assignment['due_at'] else '',
                       ', '.join(assignment['submission_types']),
                       assignment['points_possible'] if assignment['points_possible'] else '',
                       rubric_has_criteria,
                       rubric_has_clos,
                       'X' if 'group_category_id' in assignment and assignment['group_category_id'] else '',
                       ', '.join([p['name'] for p in get_course_people(course_id, 'Faculty of record')])]
                rows.append(row)
                print(row)

    write_xlsx_file('turnitin_api_assignments_summer_{}'
                    .format(datetime.now().strftime('%Y.%m.%d.%H.%M.%S')), header, rows)

if __name__ == '__main__':
    turnitin_api_assignments()
    tada()
