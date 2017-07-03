import re

import core.config as config
import mammoth
from canvas.core.accounts import program_account
from canvas.core.constants import term_id_from_name
from canvas.core.courses import get_courses, validate_course
from canvas.core.outcome_groups import get_root_group
from canvas.core.outcomes import get_outcomes, link_new_outcome

from canvas.core.io import tada


def push_genomics_to_courses():
    term = '2016SPRING'
    program = 'DNP'
    document_title = 'glos_dnp.docx'

    # read genomic resources from Word document, convert to HTML, and load dict
    glos = {}
    with open(document_title, 'rb') as docx_file:
        html = mammoth.convert_to_html(docx_file).value
    for page in html.split('!!!'):
        match_result = re.match(r'^(.*?)</p>(.*)<p>$', page)
        if match_result:
            glo_id, text = match_result.group(1), match_result.group(2)
            course_number = glo_id.split('_')[0]
            if course_number not in glos:
                glos[course_number] = []
            glos[course_number].append([glo_id, text])
        else:
            print('>>>>', page)

    title_roots = {}
    term_id = term_id(term)
    account = program_account(program)
    for course in get_courses(account, term_id):

        # validate course
        course_number = validate_course(course, program)
        if not course_number:
            continue

        # skip if no GLOs
        if course_number not in glos:
            continue

        # print(leader, 'https://samuelmerritt.{}instructure.com/courses/{}/outcomes'
        #       .format('test.' if config.env == 'test' else '', course_id))

        course_id, course_sis_id = course['id'], course['sis_course_id']
        leader = '{: <10}{: <40}'.format(program, course_sis_id)

        # get course CLOs
        course_root_group = get_root_group('courses', course_id)
        course_clos = get_outcomes('courses', course_id, course_root_group)
        if not course_clos:
            print(leader, '>>> no clos found in course:')
            continue

        # skip if course already has GLOs ************* DOES THIS WORK? FALL HAD DUPLICATE GLOS! ***************
        pushed = False
        for course_clo in course_clos:
            if 'Genomics' in course_clo['title']:
                pushed = True
                print(leader, '>>> {} already pushed'.format(course_clo['title']))
                break
        if pushed:
            continue

        # determine whether existing CLO title format is Nxxx or Nxxx/xxxL
        if course_number not in title_roots:
            # get CLO title root from first CLO
            clo_title = course_clos[0]['title']
            match_result = re.match(r'^CLO (.*)_.*$', clo_title)
            title_roots[course_number] = match_result.group(1)

        # push the GLOs
        for glo in glos[course_number]:
            glo_title, text = (i for i in glo)
            glo_title = '{}_{} Genomics'.format(title_roots[course_number], glo_title.split('_')[1])
            print(leader, glo_title)
            link_new_outcome('courses', course_id, course_root_group, glo_title, text)


if __name__ == '__main__':
    push_genomics_to_courses()
    tada()
