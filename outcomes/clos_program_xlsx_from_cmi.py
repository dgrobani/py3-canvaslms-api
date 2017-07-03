import canvas.core.io as io
import xlsxwriter
from canvas.core.accounts import all_programs

from canvas.core.etc import scrub

programs = []
for program in programs or all_programs('fnp_online_no'):
    query = ('SELECT c.CourseID AS course_id, c.CLO_ID AS clo_title, c.CLO AS clo_description ' +
             'FROM Courses c WHERE c.programID = "' + program + '" AND c.Active = 1 AND c.CLO NOT LIKE "%deleted%"')
    cmi_records = io.get_db_query_results('cmi', query)[0]
    workbook = xlsxwriter.Workbook('CLOs_{}_2015.09.09.xlsx'.format(program))
    previous_course_id = ''
    for row_number, cmi_record in enumerate(cmi_records):
        current_course_id = cmi_record['course_id'].replace('-', '')
        course_id = cmi_record['course_id']
        clo_title = cmi_record['clo_title'].replace('-', '')
        clo_desc = scrub(cmi_record['clo_description'])
        if current_course_id != previous_course_id:
            worksheet = workbook.add_worksheet(cmi_record['clo_title'].replace('-', '').replace('/', '-'))
            for column_number, column_header in enumerate(['course', 'CLO name', 'CLO description']):
                worksheet.write(0, column_number, column_header)
            print(program, course_id)
        for column_number, column_data in enumerate([course_id, clo_title, clo_desc]):
            worksheet.write(row_number + 1, column_number, column_data)
        print(clo_title, clo_desc)
        previous_course_id = current_course_id
    workbook.close()
