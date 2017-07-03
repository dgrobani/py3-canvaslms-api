from datetime import datetime

from canvas.core.accounts import program_account, all_programs
from canvas.core.courses import get_course_people, get_courses, validate_course, get_course_modules, \
    get_course_announcements, get_course_files, get_course_pages, get_course_syllabus_body, get_course_conferences, \
    get_course_tabs
from canvas.core.io import tada, write_xlsx_file
from canvas.core.terms import term_id_from_name, all_terms

from canvas.core.assignments import get_assignment_groups, assignment_is_graded


### add course_front_page_set()

def course_inventory_and_alignments():
    course_whitelist = []
    terms = ['DEFAULT']
    programs = []

    for term in terms or all_terms():

        term_id = term_id_from_name(term)

        for program in programs or all_programs('synergis_yes'):

            account = program_account(program)
            courses = get_courses(account, term_id)
            rows = []
            max_teachers = 0

            for course in courses:

                course_sis_id = course['sis_course_id']
                if course_whitelist and course_sis_id not in course_whitelist:
                    continue

                # omit unpublished and clinical courses
                course_sis_info = validate_course(course)
                # if not course_sis_info or not course_is_published(course) or course_sis_info['number'].endswith('L'):
                if not course_sis_info:
                    continue

                course_id = course['id']

                # course-level conditions
                syllabus = get_course_syllabus_body(course_id)
                syllabus_has_link_or_length = syllabus is not None and ('href' in syllabus or len(syllabus) > 600)
                assignment_group_weights = course['apply_assignment_group_weights']

                # course-level counts
                announcement_qty = len(get_course_announcements(course_id))
                conference_qty = len(get_course_conferences(course_id))
                file_qty = len(get_course_files(course_id))
                page_qty = len(get_course_pages(course_id))
                student_qty = len(get_course_people(course_id, 'student'))
                teachers = get_course_people(course_id, 'teacher')
                teacher_qty = len(teachers)

                # tabs
                tab_qty = 0
                tabs_pages_and_files_hidden = True
                for tab in get_course_tabs(course_id):
                    if 'hidden' not in tab:
                        tab_qty += 1
                        if tab['label'] in ['Pages', 'Files']:
                            tabs_pages_and_files_hidden = False

                # modules
                modules = get_course_modules(course_id)
                module_qty = len(modules)
                module_has_items_qty = 0
                for module in modules:
                    module_has_items_qty += (module['items_count'] > 0)

                # assignment groups
                assignment_groups = get_assignment_groups(course_id)
                assignment_group_qty = len(assignment_groups)
                assignment_group_has_assignments_qty = 0

                # assignments
                assignment_qty = 0
                quiz_qty = 0
                discussion_qty = 0
                assignment_or_discussion_with_ok_body_qty = 0
                assignment_with_rubric_qty = 0
                assignment_with_alignments_qty = 0

                for assignment_group in assignment_groups:
                    assignments = assignment_group['assignments']
                    assignment_group_has_assignments_qty += (len(assignments) > 0)

                    for assignment in assignments:
                        # print(course_sis_id, assignment['submission_types'], assignment['name'],
                        #       assignment['points_possible'])
                        if not assignment_is_graded(assignment):
                            continue
                        if 'online_quiz' in assignment['submission_types']:
                            assignment_type = 'quiz'
                            quiz_qty += 1
                        elif 'discussion_topic' in assignment['submission_types']:
                            assignment_type = 'discussion'
                            discussion_qty += 1
                        else:
                            assignment_type = 'assignment'
                            assignment_qty += 1

                        assignment_body = assignment['description']
                        if assignment_type != 'quiz' and assignment_body is not None and \
                                (len(assignment_body) > 100 or 'href' in assignment_body):
                            assignment_or_discussion_with_ok_body_qty += 1

                        if 'rubric' in assignment:
                            assignment_with_rubric_qty += 1
                            for criterion in assignment['rubric']:
                                if 'outcome_id' in criterion:
                                    assignment_with_alignments_qty += 1
                                    break

                row = [
                    program,
                    term,
                    course_sis_info['session'],
                    course_sis_info['campus'],
                    course_sis_info['number'],
                    course_sis_info['type'],
                    course_sis_info['section'],
                    course_sis_id,
                    'http://samuelmerritt.instructure.com/courses/{}'.format(course_id),
                    tab_qty,
                    tabs_pages_and_files_hidden,
                    syllabus_has_link_or_length,
                    module_qty,
                    module_has_items_qty,
                    assignment_group_weights,
                    assignment_group_qty,
                    assignment_group_has_assignments_qty,
                    quiz_qty,
                    assignment_qty,
                    discussion_qty,
                    assignment_or_discussion_with_ok_body_qty,
                    assignment_with_rubric_qty,
                    assignment_with_alignments_qty,
                    announcement_qty,
                    conference_qty,
                    page_qty,
                    file_qty,
                    student_qty,
                    teacher_qty
                ]
                row.extend([t['sortable_name'] for t in teachers])
                print(row)
                rows.append(row)
                max_teachers = max(max_teachers, teacher_qty)

            header = [
                'program',
                'term',
                'session',
                'campus',
                'course number',
                'type',
                'section',
                'course sis id',
                'URL',
                'tabs',
                'tabs hidden: Pages & Files',
                'syllabus has link',
                'modules',
                'modules with items',
                'assignment group weights affect final grade',
                'assignment groups',
                'assignment groups with assignments',
                'graded quizzes',
                'graded assignments',
                'graded discussions',
                'graded assignments/discussions with body > 100 characters or link',
                'graded assignments/discussions/quizzes with rubrics',
                'graded assignments/discussions/quizzes with alignments',
                'announcements',
                'conferences',
                'pages',
                'files',
                'students',
                'teachers'
            ]
            # add teacher column headers and pad data rows
            header.extend('teacher{0:0>2}'.format(i + 1) for i in range(max_teachers))
            for row in rows:
                row.extend([''] * (len(header) - len(row)))

            write_xlsx_file('canvas_course_inventory_{}_{}_{}'
                            .format(term, program, datetime.now().strftime("%Y%m%d.%H%M%S")), header, rows)


if __name__ == '__main__':
    course_inventory_and_alignments()
    tada()
