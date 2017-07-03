from canvas.core import config
from canvas.core.io import run_sql_file, tada, sis_import, write_csv_file


def batch_enrollments(sql_filename, csv_filename):
    rows, column_names = run_sql_file('powercampus', sql_filename)
    write_csv_file(csv_filename, column_names, rows)
    records = open(config.output_dir + csv_filename, 'r').read()
    print('sending {} records returned by {}...'.format(len(rows), sql_filename))
    sis_import(records)
    print('\n\timported!')


batch_enrollments('batch_enrollments_1.sql', 'batch_enrollments_1.csv')
batch_enrollments('batch_enrollments_2.sql', 'batch_enrollments_2.csv')
tada()
