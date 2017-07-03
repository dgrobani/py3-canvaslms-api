# http://pbpython.com/python-word-template.html
# https://github.com/awslabs/aws-python-sample/blob/master/s3_sample.py
# http://boto3.readthedocs.io/en/latest/guide/migrations3.html
# https://vverma.net/scrape-the-web-using-css-selectors-in-python.html
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/

import datetime
import re
from collections import defaultdict

import boto3
from bs4 import BeautifulSoup
from mailmerge import MailMerge

from canvas.core import config
from canvas.core.accounts import catalog_program, program_formal_name, get_account_grading_standard, \
    program_account
from canvas.core.assignments import get_assignment_groups
from canvas.core.courses import get_courses, get_course_modules, get_onl_masters, \
    get_course_module_items, get_course_front_page
from canvas.core.io import get_cmi_plos_by_program, get_db_query_results, tada, get_cmi_clos_by_course
from canvas.core.outcomes import get_outcome


def main():
    course_whitelist = [
        '2017-1SP-01-PT-743-LEC-OAK-01',
        '2017-1SP-01-NFNP-676-LEC-SAC-01'
    ]
    terms = ['2017-2SU']
    programs = []

    if 'NFNPO' in programs or 'NCMO' in programs:
        for term in terms:
            for program in programs:
                for master in get_onl_masters(program):
                    syllabus_template(master, program, term)
    else:
        for course in get_courses(terms, programs, False, course_whitelist):
            syllabus_template(course)


def syllabus_template(l_course, l_program='', l_term=''):
    course_id = l_course['id']
    basics = get_basics(l_course, l_program, l_term)
    required_materials = get_onl_course_materials(course_id) if l_program else []
    clos = get_cmi_clos_by_course(basics['program'], basics['course_number'])
    plos = get_cmi_plos_by_program(basics['program'])
    assignment_groups, assignment_group_names, assignment_assignment_groups, assignment_clos = \
        get_assignments(course_id)
    module_assignments = get_modules(course_id, assignment_group_names, assignment_assignment_groups, assignment_clos)
    group_weights, group_weights_total = get_assignment_group_weights(assignment_groups)
    grading_standard = get_grading_standard(l_course['account_id'])
    write_file(basics, required_materials, clos, plos, module_assignments, group_weights, group_weights_total,
               grading_standard)
    write_file(basics, required_materials, [], [], module_assignments, group_weights, group_weights_total,
               grading_standard)
    upload_file(basics['out_filename'])


def get_basics(l_course, l_program, l_term):

    basics = {}

    if l_program:
        basics['program'] = l_program
        basics['term'] = l_term
        basics['course_number'] = l_course['name'].split(' ')[0].replace(':', '')
        print(l_program, basics['course_number'])
        basics['footer_section'] = ''
        basics['in_filename'] = 'syllabot_onl.docx'
        basics['out_filename'] = 'syllabot_ONL_{}_{}.docx'.format(l_program, basics['course_number'])

    else:
        sis_id = l_course['sis_course_id']
        print(sis_id)
        course_sis_info = l_course['course_sis_info']
        basics['program'] = course_sis_info['program']
        basics['term'] = course_sis_info['term']
        basics['course_number'] = course_sis_info['number']
        basics['section'] = 'Section ' + course_sis_info['section']
        basics['footer_section'] = ''

        basics['office_location'] = 'Office location:'
        basics['meeting_times'] = 'Meeting times:'
        basics['class_location'] = 'Location:'
        basics['in_filename'] = 'syllabot.docx'
        basics['out_filename'] = 'syllabot_{}.docx'.format(sis_id)

    basics['term'] = ['Spring', 'Summer', 'Fall'][int(basics['term'][5]) - 1] + ' ' + basics['term'][0:4]
    basics['program_name'] = program_formal_name(basics['program'])
    basics['program_prefix'] = \
        'GENED' if basics['course_number'].startswith('GE') else catalog_program(basics['program'])
    basics['catalog_course_number'] = derive_catalog_course_number(basics['program_prefix'], basics['course_number'])
    basics['name'], basics['description'], basics['credits'] = get_powercampus_data(basics['catalog_course_number'])

    return basics


def derive_catalog_course_number(program_prefix, course_number):
    exceptions = {'NURSG 100': 'IPE 100', 'NURSG 104': 'GENED 104', 'NURSG 433': 'GENED 433',
                  'NURSG 442': 'GENED 442', 'NURSG 456': 'GENED 456'}
    catalog_course_number = program_prefix + ' ' + re.sub(r'^\D*', '', course_number)
    return exceptions[catalog_course_number] if catalog_course_number in exceptions else catalog_course_number


def get_powercampus_data(catalog_course_number):

    TODO: begin, end, drop dates
    query = 'SELECT start_date, end_date FROM sections WHERE academic_year = {} AND academic_term = {} AND ' \
            'event_id = {} AND event_sub_type = {} AND section = {} AND curriculum = {}' \
        .format(catalog_course_number)
    pc_data = get_db_query_results('powercampus', query)[0][0]

    query = 'SELECT event_long_name, description, credits FROM event WHERE EVENT_ID = \'{}\''\
        .format(catalog_course_number)
    results = get_db_query_results('powercampus', query)[0]
    if not results:
        print('>>>>> NO POWERCAMPUS EVENT FOR ' + catalog_course_number)
        return '???', '???', '???'
    pc_data = results[0]
    name = pc_data[0]
    description = pc_data[1]
    creditz = '{0:.2f}'.format(pc_data[2])
    return name, description, creditz


def get_assignments(course_id):
    assignment_assignment_groups = defaultdict(str)
    assignment_group_names = defaultdict(str)
    assignment_clos = defaultdict(list)
    assignment_groups = get_assignment_groups(course_id)
    for assignment_group in assignment_groups:
        assignment_group_names[assignment_group['id']] = assignment_group['name']
        for assignment in assignment_group['assignments']:
            assignment_assignment_groups[assignment['id']] = assignment_group['id']
            if 'rubric' in assignment:
                assignment_clos[assignment['id']] = \
                    [get_outcome(criterion['outcome_id'])['title']
                     for criterion in assignment['rubric'] if 'outcome_id' in criterion]
    return assignment_groups, assignment_group_names, assignment_assignment_groups, assignment_clos


def get_modules(course_id, assignment_group_names, assignment_assignment_groups, assignment_clos):
    module_assessments = []
    for course_module in get_course_modules(course_id):
        printed_module_name = False
        for item in get_course_module_items(course_id, course_module):
            if item['type'] in ['Discussion', 'Assignment', 'Quiz', 'ExternalTool']:
                if printed_module_name:
                    module_name = ''
                else:
                    module_name = course_module['name']
                    printed_module_name = True
                module_assessments.append(
                    {'module_name': module_name,
                     'assignment_name': item['title'],
                     'assignment_group': assignment_group_names[assignment_assignment_groups[item['content_id']]],
                     'assignment_clos': ', '.join(assignment_clos[item['content_id']])
                     })
        if not printed_module_name:
            module_assessments.append({'module_name': course_module['name']})
    return module_assessments


def get_assignment_group_weights(l_assignment_groups):
    weights = [{'assignment_group_name': group['name'], 'assignment_group_percent': str(group['group_weight'])}
               for group in l_assignment_groups]
    total = str(sum([group['group_weight'] for group in l_assignment_groups]))
    return weights, total


def get_grading_standard(account_id):
    l_grading_standard = []
    high_value = 100
    for scheme_item in get_account_grading_standard(account_id)[0]['grading_scheme']:
        low_value = int(scheme_item['value'] * 100)
        l_grading_standard.append({'grading_scale_high': str(high_value),
                                   'grading_scale_low': str(low_value),
                                   'grading_scale_letter': scheme_item['name']})
        high_value = low_value - 1
    return l_grading_standard


def get_onl_course_materials(course_id):
    required_materials = []
    return required_materials


def write_file(l_basics, l_materials, l_clos, l_plos, assignments, weights, weights_total, standard):
    template = MailMerge(l_basics['in_filename'])
    template.merge(
        program_name=l_basics['program_name'],
        course_number=l_basics['catalog_course_number'],
        course_name=l_basics['name'],
        term=l_basics['term'],
        course_description=l_basics['description'],
        credits=l_basics['credits'],
        assignment_group_total=weights_total,
        footer_course_number=l_basics['catalog_course_number'],
        footer_term=l_basics['term'],
        footer_section=l_basics['footer_section'],
        footer_date=datetime.date.today().strftime('%m/%d/%Y'))
    if l_basics['program'] not in ['NFNPO', 'NCMO']:
        template.merge(
            section=l_basics['section'],
            office_location=l_basics['office_location'],
            meeting_times=l_basics['meeting_times'],
            class_location=l_basics['class_location'])
    template.merge_rows('required_title', l_materials)
    template.merge_rows('clo_title', l_clos)
    template.merge_rows('plo_title', l_plos)
    template.merge_rows('module_name', assignments)
    template.merge_rows('assignment_group_name', weights)
    template.merge_rows('grading_scale_high', standard)
    template.write(config.output_dir + l_basics['out_filename'])


def upload_file(syllabus_filename):
    s3 = boto3.client('s3', aws_access_key_id=config.aws_access_key_id,
                      aws_secret_access_key=config.aws_secret_access_key)
    s3.upload_file(config.output_dir + syllabus_filename, 'smu-aii', 'syllabi/' + syllabus_filename)


if __name__ == '__main__':
    main()
    tada()
