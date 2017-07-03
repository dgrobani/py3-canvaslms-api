import xlsxwriter
from canvas.core.outcome_groups import get_root_group, get_subgroups
from canvas.core.outcomes import get_outcomes

from canvas.core.accounts import program_account, all_programs

programs = []
for program in programs or all_programs('fnp_online_no'):
    program_workbook = xlsxwriter.Workbook('CLOs_{}_2015.09.09.xlsx'.format(program))
    account = program_account(program)
    program_root_group_id = get_root_group('accounts', account)
    for course_group in get_subgroups('accounts', account, program_root_group_id):
        course_worksheet = program_workbook.add_worksheet(course_group['title'].replace('/', '-'))
        for column_number, column_header in enumerate(['course', 'CLO name', 'CLO description']):
            course_worksheet.write(0, column_number, column_header)
        for row, clo in enumerate(get_outcomes('accounts', account, course_group['id'])):
            for column_number, column_data in enumerate([course_group['title'], clo['title'], clo['description']]):
                course_worksheet.write(row + 1, column_number, column_data)
            print(course_group['title'], clo['title'], clo['description'])
    program_workbook.close()
