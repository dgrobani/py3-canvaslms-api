#
# review https://canvas.instructure.com/doc/api/enrollments.html#method.enrollments_api.index, which returns grades
#

from canvas.core.accounts import program_account, all_programs
from canvas.core.courses import get_course_people, get_courses, validate_course
from canvas.core.io import tada, write_csv_file

from canvas.core.assignments import get_assignment_student_grades, get_assignments
from canvas.core.assignments import get_assignments


def grades_export():

    #course_whitelist = ['2015SS-OAK-GENERAL-NURSG-128-LEC1-1']
    course_whitelist = []
    programs = ['BSN']
    term = '2015SPRING'
    term_id = term_id(term)

    for program in programs or all_programs('fnp_online_yes'):
        rows = []
        account = program_account(program)
        for course in get_courses(account, term_id):

            # skip unpublished courses
            if course['workflow_state'] not in ['available', 'completed']:
                continue

            if course_whitelist and course['sis_course_id'] not in course_whitelist:
                continue

            course_number = validate_course(course, program)
            if not course_number:
                continue

            course_id = course['id']

            # store each assignment's type
            assignment_type = {}
            for assignment in get_assignments(course_id):
                assignment_type[assignment['id']] = assignment["submission_types"]

            # get each student's assignments & grades
            for student in get_course_people(course_id, 'student'):
                assignment_grades = get_assignment_student_grades(course_id, student['id'])
                for assignment_grade in assignment_grades:
                    if 'submission' in assignment_grade:
                        submission_time = assignment_grade['submission']['submitted_at']
                        submission_score = assignment_grade['submission']['score']
                    else:
                        submission_score = 'NULL'
                        submission_time = 'NULL'

                    row = [program,
                           course['sis_course_id'],
                           student['sortable_name'],
                           student['sis_user_id'],
                           assignment_type[assignment_grade['assignment_id']],
                           assignment_grade['title'],
                           submission_time,
                           submission_score,
                           assignment_grade['points_possible']
                           ]
                    print(row)
                    rows.append(row)
#################
                break
#################
        write_csv_file('canvas_grades_{}_{}.csv'.format(term, program),
                       ['program',
                        'course',
                        'student name',
                        'student id',
                        'activity type',
                        'activity name',
                        'activity datetime',
                        'points received',
                        'points possible'],
                       rows)


if __name__ == '__main__':
    grades_export()
    tada()
