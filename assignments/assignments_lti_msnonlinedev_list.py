from datetime import datetime

from canvas.core.assignments import get_assignments
from canvas.core.courses import get_courses_by_account_id
from canvas.core.io import tada, write_xlsx_file

accounts = {'DEV FNPO': '168920', 'DEV CMO': '168922'}
# header = ['program', 'course name', 'lti', 'assignment name', 'assignment URL']
header = ['program', 'course name', 'assignment name', 'assignment URL', 'rubric length']
rows = []
for account in accounts:
    for course in get_courses_by_account_id(accounts[account], 'DEFAULT'):
        if course['account_id'] not in [168920, 168922]:
            continue
        course_id = course['id']
        for assignment in get_assignments(course_id):
            # if 'external_tool' in assignment['submission_types']:
            if 'rubric' in assignment:
                print(assignment['rubric'])
                # lti_type = 'turnitin' if 'turnitin' in assignment['external_tool_tag_attributes']['url'] \
                #     else 'youseeu' if 'youseeu' in assignment['external_tool_tag_attributes']['url'] else ''
                # row = [account, course['name'], lti_type, assignment['name'], assignment['html_url']]
                row = [account, course['name'], assignment['name'], assignment['html_url'], len(assignment['rubric'])]
                rows.append(row)
                # print(row)

# write_xlsx_file('lti_assignments_msonline_dev_{}'
write_xlsx_file('lti_rubrics_msonline_dev_{}'
                .format(datetime.now().strftime('%Y.%m.%d.%H.%M.%S')), header, rows)

tada()
