import csv
import time
import winsound

import pymysql
import pypyodbc
import xlsxwriter

from canvas.core import config
from canvas.core.accounts import cmi_program, program_account
from canvas.core.terms import term_id_from_name
import canvas.core.api as api


def get_db_query_results(db, query):
    """ connect to database; execute query; return a list of the results and a list of column names """
    if db == 'cmi':
        connection = pymysql.connect(config.cmi_host, config.cmi_user, config.cmi_pw, config.cmi_db)
    elif db == 'powercampus':
        connection = pypyodbc.connect(config.powercampus_connection_string)
    else:
        return None
    cursor = connection.cursor()
    cursor.execute(query)
    column_names = [column[0] for column in cursor.description]
    rows = [list(row) for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    # return [dict(zip(column_names, list(row))) for row in rows]
    return rows, column_names


def get_cmi_clos_by_program(canvas_program):
    query = ('SELECT c.CourseID AS course_id, c.CLO_ID AS clo_title, c.CLO AS clo_description ' +
             'FROM Courses c WHERE c.programID = "' + cmi_program(canvas_program) +
             '" AND c.Active = 1 AND c.CLO NOT LIKE "%deleted%"')
    return [{'course_id': clo[0], 'clo_title': clo[1], 'clo_description': clo[2]}
            for clo in get_db_query_results('cmi', query)[0]]


def get_cmi_clos_by_course(canvas_program, course_name):
    query = ('SELECT REPLACE(c.CLO_ID, "-", "" ) AS clo_title, c.CLO AS clo_description ' +
             'FROM Courses c WHERE c.programID = "' + cmi_program(canvas_program) +
             '" AND REPLACE(c.CourseID, "-", "" ) = "' + course_name +
             '" AND c.Active = 1 AND c.CLO NOT LIKE "%deleted%"')
    return [{'clo_title': clo[0], 'clo_description': clo[1]} for clo in get_db_query_results('cmi', query)[0]]


def get_cmi_plos_by_program(canvas_program):
    query = ('SELECT p.SLOID AS plo_title, p.SLOName AS plo_description FROM programSLOList p WHERE p.programID = "' +
             cmi_program(canvas_program) + '" AND p.Active = 1')
    return [{'plo_title': plo[0], 'plo_description': plo[1]} for plo in get_db_query_results('cmi', query)[0]]


def run_sql_file(db, sql_file_name, sql_dir=config.sql_dir):
    """ run sql from a file, return rows and column names """
    with open(sql_dir + sql_file_name) as sql_file:
        query = sql_file.read()
    return get_db_query_results(db, query)


def write_csv_file(file_name, header_row, data_rows, out_dir=config.output_dir):
    """ write a header row and all data rows to a csv file """
    with open(out_dir + file_name, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        csv_writer.writerow(header_row)
        for row in data_rows:
            csv_writer.writerow(row)


def write_xlsx_file(file_name, header_row, data_rows):
    """ write a table to an xlsx file per http://xlsxwriter.readthedocs.org/working_with_tables.html """
    workbook = xlsxwriter.Workbook('{}{}.xlsx'.format(config.output_dir, file_name))
    workbook.add_worksheet().add_table(0, 0, len(data_rows), len(header_row) - 1,
                                       {'data': data_rows, 'columns': [{'header': i} for i in header_row]})
    workbook.close()


def sis_import(sis_data):
    # https://github.com/kajigga/canvas-contrib/blob/master/SIS%20Integration/python_requestlib/import_csv.py
    # https://github.com/bryanpearson/canvas-sis-python/blob/master/canvas_sis_import.py
    get_url = 'accounts/{}/sis_imports'.format(config.root_account)
    post_url = get_url + '?import_type=instructure_csv&extension=csv'
    r = api.post(post_url, sis_data)
    while not api.get('{}/{}'.format(get_url, str(r.json()['id']))).json()['ended_at']:
        wait('\twaiting for import confirmation', 30)


def get_sis_report(report_type, account, term, mode):
    """ request sis report; return list of column names & list of results """
    # https://github.com/unsupported/canvas/tree/master/api/run_reports/provisioning_report/python
    # https://community.canvaslms.com/thread/11942
    account_id = program_account(account)
    req_data = {'parameters[enrollment_term_id]': term_id_from_name(term), 'parameters[{}]'.format(report_type): 1}
    report_id = api.post('accounts/{}/reports/sis_export_csv'.format(account_id), req_data).json()['id']
    progress = 0
    while progress < 100:
        response = api.get('accounts/{}/reports/sis_export_csv/{}'.format(account_id, report_id))
        json = response.json()
        progress = json['progress']
        wait('\tprogress: {}%'.format(progress), 5)
    content = api.get_file(json['attachment']['url']).content
    if mode == 'file':
        with open(config.output_dir + json['attachment']['filename'], 'wb') as file:
            file.write(content)
    rows = [x for x in sorted(csv.reader(str(content, 'utf-8').split('\n')))]
    # remove extra EOL as last line
    return rows[0], rows[1:-1]


def wait(msg, interval):
    if msg:
        print('\r{}....'.format(msg), end="")
    time.sleep(interval)


def tada():
    winsound.Beep(700, 500)
    winsound.Beep(800, 500)
    winsound.Beep(900, 500)


def print_pretty(*argv):
    print('{} {: >19} {: <17} {}'.format(*argv))
