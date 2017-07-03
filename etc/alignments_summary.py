from canvas.core.accounts import program_account, all_programs
from canvas.core.courses import get_course_people, get_courses, parse_course_sis, validate_course
from canvas.core.io import tada, write_csv_file, write_xlsx_file
from canvas.core.terms import all_terms

from canvas.core.assignments import get_assignment_groups


def alignments_summarize():
    # whitelist = ['2015FS-OAK-GRAD-PHYTH-756-LEC-1']
    course_whitelist = []
    programs = []
    terms = ['2016SPRING']
    rows_summary = []
    rows_detail = []
    max_teachers = 0
    for term in terms or all_terms():
        term_id = term_id(term)
        for program in programs or all_programs('fnp_online_yes'):
            account = program_account(program)
            courses = get_courses(account, term_id)
            course_qty = len(courses)
            rubricked_course_qty = 0
            aligned_course_qty = 0
            total_assignment_qty = 0
            total_rubricked_assignment_qty = 0
            total_aligned_assignment_qty = 0
            rows_csv = []
            for course in courses:

                if course_whitelist and course['sis_course_id'] not in course_whitelist or not validate_course(course):
                    continue

                assignment_qty = 0
                rubricked_assignment_qty = 0
                aligned_assignment_qty = 0
                course_id = course['id']
                for assignment_group in get_assignment_groups(course_id):
                    assignment_qty += len(assignment_group['assignments'])
                    for assignment in assignment_group['assignments']:
                        if 'rubric' in assignment:
                            rubricked_assignment_qty += 1
                            for criterion in assignment['rubric']:
                                if 'outcome_id' in criterion:
                                    aligned_assignment_qty += 1
                                    break

                course_sis_info = parse_course_sis(course['sis_course_id'])
                teachers = get_course_people(course_id, 'teacher')
                max_teachers = max(max_teachers, len(teachers))
                row = [term, program, course_sis_info['number'],
                       ', '.join(teacher['sortable_name'] for teacher in teachers),
                       assignment_qty, rubricked_assignment_qty, aligned_assignment_qty]
                rows_csv.append(row)
                print(row)

                rubricked_course_qty += (rubricked_assignment_qty > 0)
                aligned_course_qty += (aligned_assignment_qty > 0)
                total_assignment_qty += assignment_qty
                total_rubricked_assignment_qty += rubricked_assignment_qty
                total_aligned_assignment_qty += aligned_assignment_qty

                rows_detail.append({
                    'term': term,
                    'program': program,
                    'course_number': course_sis_info['number'],
                    'course_campus': course_sis_info['campus'],
                    'course_type': course_sis_info['type'],
                    'course_section': course_sis_info['section'],
                    'teachers': teachers,
                    'quantities': [assignment_qty, rubricked_assignment_qty, aligned_assignment_qty],
                    'booleans': ['No' if assignment_qty == 0 else 'Yes',
                                 'No' if rubricked_assignment_qty == 0 else 'Yes',
                                 'No' if aligned_assignment_qty == 0 else 'Yes']})

            # write csv file with totals
            rows_csv.append([term, program, '', 'totals', total_assignment_qty, total_rubricked_assignment_qty,
                             total_aligned_assignment_qty, course_qty, rubricked_course_qty, aligned_course_qty])
            header = ['term', 'program', 'course', 'teachers', 'assignments', 'rubricked assignments',
                      'aligned assignments', 'courses', 'rubricked courses', 'aligned courses']
            write_csv_file('alignments_{}_{}.csv'.format(term, program), header, rows_csv)

            rows_summary.append([term, program,
                                 total_assignment_qty,
                                 '{0:.0f}'.format(total_rubricked_assignment_qty / total_assignment_qty * 100)
                                 if total_assignment_qty > 0 else '0',
                                 '{0:.0f}'.format(total_aligned_assignment_qty / total_assignment_qty * 100)
                                 if total_assignment_qty > 0 else '0'])

        # write summary xlsx file [penny]
        header = ['term', 'program', 'assignments', '% with rubrics', '% aligned']
        write_xlsx_file('alignments_{}_summary'.format(term), rows_summary, header)

        # write detail xlsx file without totals [nandini]
        rows_detail_out = []
        for row in rows_detail:
            rows_detail_out.append([row['term'], row['program'], row['course_number'], row['course_campus'],
                                    row['course_type'], row['course_section']])
            rows_detail_out[-1].extend([t['sortable_name'] for t in row['teachers']])
            rows_detail_out[-1].extend([''] * (max_teachers - len(row['teachers'])))
            rows_detail_out[-1].extend(row['quantities'])
            rows_detail_out[-1].extend(row['booleans'])
        header_detail = ['term', 'program', 'course', 'campus', 'type', 'section']
        header_detail.extend('teacher{0:0>2}'.format(i + 1) for i in range(max_teachers))
        header_detail.extend(['assignments', 'rubricked assignments', 'aligned assignments',
                              'course has assignments in canvas', 'course has assignments with rubrics',
                              'course has assignments aligned to CLOs'])
        write_xlsx_file('alignments_{}_detail'.format(term), rows_detail_out, header_detail)


if __name__ == '__main__':
    alignments_summarize()
    tada()
