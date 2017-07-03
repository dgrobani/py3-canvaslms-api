from canvas.core.courses import create_enrollment, get_course_by_sis_id, get_course_people
from canvas.core.io import tada
from canvas.core.terms import term_id_from_name

from canvas.core.api import get_list


def batch_enroll_nursing_community_courses():

    term = '2016-1SP'
    nursing_account = '98328'
    nursing_community_course_sis_ids = ['COMM-NURSG-DEPT', 'COMM-NURSG-FAC-RESOURCE', 'COMM-NURSG-GERI-PRO']

    # get teachers enrolled in nursing courses
    account_courses = \
        get_list('accounts/{}/courses?enrollment_term_id={}&enrollment_type[]=teacher&include[]=teachers'
                 .format(nursing_account, term_id_from_name(term)))
    nursing_teachers = set()
    for course in account_courses:
        # print(course['sis_course_id'])
        # for teacher in course['teachers']:
        #     print(teacher['display_name'])
        #     nursing_teachers.add(teacher['id'])
        nursing_teachers.add([t['id'] for t in course['teachers']])

    # enroll as student in each community course those nursing teachers not already enrolled
    for course_sis_id in nursing_community_course_sis_ids:
        course_id = get_course_by_sis_id(course_sis_id)['id']
        # community_students = set()
        # for community_student in get_course_people(course_id, 'student'):
        #     community_students.add(community_student['id'])
        community_students = set([s['id'] for s in get_course_people(course_id, 'student')])
        # for teacher_id in nursing_teachers:
        #     if teacher_id not in community_students:
        #         # create_enrollment(course_id, user_id, 'student')
        #         print(course_sis_id, nursing_teachers[teacher_id])
        for teacher_id in nursing_teachers - community_students:
            create_enrollment(course_id, teacher_id, 'student')
            # print(course_sis_id, nursing_teachers[teacher_id])

if __name__ == '__main__':
    batch_enroll_nursing_community_courses()
    tada()
